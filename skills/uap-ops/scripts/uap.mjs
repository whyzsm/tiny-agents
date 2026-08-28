#!/usr/bin/env node
/**
 * UAP Ops CLI（uap-ops，独立版；源出 xiaoneng op-uap-ops）
 *
 * 直连公司 UAP（统一授权平台：菜单 / 功能点 / 赋权）的零依赖命令行工具。
 * 不依赖 @ane/uap-mcp npm 包，也不依赖 MCP stdio：直接经 AgentForge MCP Gateway
 * （Streamable HTTP + JSON-RPC 2.0）调用 UAP 白名单工具。
 *
 * 业务语义与安全约束移植自 @ane/uap-mcp 源码 dist/（内网 npm 包），
 * 包括：入参 strict 校验、大结果只在进程内消化、角色赋权祖先勾选重算、
 * 无实际变化不调用写接口、功能点 parentResId 用页面菜单 id。
 *
 * 网关配置（不入库）：
 *   - 环境变量 UAP_GATEWAY_URL + UAP_GATEWAY_APP_KEY（二者须同时提供）
 *   - 或本脚本同目录 uap-gateway.local.json：{ "url": "...", "appKey": "..." }
 *   - 取值来源：@ane/uap-mcp 源码 dist/infra/uap-config.js（UAP_GATEWAY）或平台组
 *   - 可选 UAP_TIMEOUT_MS（默认 30000）、UAP_APPLICATION_ALL（应用快照 json 路径）
 *
 * 用法：
 *   node uap.mjs ping
 *   node uap.mjs app-info --uap-name 天象
 *   node uap.mjs find-resource --app-id max --res-name xxx [--parent-res-name 目录名]
 *   node uap.mjs create-menu --json '{"appId":"max","resName":"页面名","resUrl":"/xxx/yyy","single":0,"parentResId":"123"}' --yes
 *   node uap.mjs create-function --json '{...}' --yes
 *   node uap.mjs update-menu --json '{...}' --yes
 *   node uap.mjs update-function --json '{...}' --yes
 *   node uap.mjs update-button --json '{...}' --yes
 *   node uap.mjs get-user-roles --app-id max [--u-id 12436] [--role-name xxx]
 *   node uap.mjs assign-user-roles --json '{...}' --yes
 *   node uap.mjs preview-role-permissions --json '{...}'
 *   node uap.mjs update-role-permissions --json '{...}' --yes
 *   node uap.mjs call <gateway-tool-name> --json '{...}'
 *
 * 输出：stdout 单个 JSON 对象；失败时 exit 1 且输出 { error:true, message, payload? }。
 * 所有写命令（create-/update-menu|function|button、assign-、update-role-permissions）
 * 必须带 --yes；执行前须先向用户展示拟变更（preview 命令或参数回读）并取得确认。
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const CLIENT_INFO = { name: 'uap-ops', version: '1.0.0' };
const PROTOCOL_VERSION = '2025-06-18';

// ---------------------------------------------------------------------------
// errors / 输出
// ---------------------------------------------------------------------------

class ServiceError extends Error {
  constructor(message, options) {
    super(message);
    this.name = 'ServiceError';
    this.payload = options?.payload;
  }
}

function stringify(payload) {
  return JSON.stringify(payload, (_key, value) => (typeof value === 'bigint' ? value.toString() : value));
}

function printOk(payload) {
  console.log(stringify(payload));
}

function printErrorAndExit(exc) {
  const body = exc instanceof ServiceError ? { error: true, message: exc.message, payload: exc.payload } : { error: true, message: exc instanceof Error ? exc.message : String(exc) };
  console.log(stringify(body));
  process.exit(1);
}

// ---------------------------------------------------------------------------
// 配置解析
// ---------------------------------------------------------------------------

function loadGatewayConfig() {
  const envUrl = process.env.UAP_GATEWAY_URL;
  const envKey = process.env.UAP_GATEWAY_APP_KEY;
  if (envUrl && envKey) return { url: envUrl, appKey: envKey };
  if (envUrl || envKey) {
    throw new ServiceError('UAP_GATEWAY_URL 与 UAP_GATEWAY_APP_KEY 须同时提供（或都不提供，改用本地配置文件）');
  }
  const localFile = path.join(SCRIPT_DIR, 'uap-gateway.local.json');
  if (fs.existsSync(localFile)) {
    try {
      const cfg = JSON.parse(fs.readFileSync(localFile, 'utf8'));
      if (cfg && typeof cfg.url === 'string' && cfg.url && typeof cfg.appKey === 'string' && cfg.appKey) {
        return { url: cfg.url, appKey: cfg.appKey };
      }
    } catch {
      // 落到下方报错
    }
  }
  throw new ServiceError('未找到网关配置。请在环境变量 UAP_GATEWAY_URL / UAP_GATEWAY_APP_KEY，或本脚本同目录 uap-gateway.local.json（{ "url": "...", "appKey": "..." }，该文件已被 gitignore）中配置 AgentForge MCP Gateway 地址与 appKey。取值见 @ane/uap-mcp 源码 dist/infra/uap-config.js 或找平台组。');
}

function timeoutMs() {
  const raw = Number(process.env.UAP_TIMEOUT_MS);
  return Number.isFinite(raw) && raw > 0 ? raw : 30_000;
}

function debugLog(...parts) {
  if (process.env.UAP_DEBUG === '1') console.error('[uap-debug]', ...parts);
}

// ---------------------------------------------------------------------------
// Streamable HTTP MCP 客户端（JSON-RPC 2.0，零依赖 fetch 实现）
// ---------------------------------------------------------------------------

class GatewayClient {
  constructor(config) {
    this.config = config;
    this.sessionId = null;
    this.protocolVersion = null;
    this.serverInfo = null;
    this.nextId = 1;
  }

  headers(extra = {}) {
    const h = {
      'Content-Type': 'application/json',
      Accept: 'application/json, text/event-stream',
      'x-app-key': this.config.appKey,
      ...extra,
    };
    if (this.protocolVersion) {
      h['MCP-Protocol-Version'] = this.protocolVersion;
    }
    return h;
  }

  async post(body, { expectResponse } = { expectResponse: true }) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs());
    let res;
    try {
      res = await fetch(this.config.url, {
        method: 'POST',
        headers: this.headers(this.sessionId ? { 'Mcp-Session-Id': this.sessionId } : {}),
        body: JSON.stringify(body),
        signal: controller.signal,
      });
    } finally {
      clearTimeout(timer);
    }
    const contentType = String(res.headers.get('content-type') || '');
    const text = await res.text();
    debugLog(`POST ${JSON.stringify(body).slice(0, 200)} -> status=${res.status} ct=${contentType} body=${text.slice(0, 200)}`);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status} ${res.statusText} ${text.slice(0, 400)}`);
    }
    if (!expectResponse) return { headers: res.headers, message: null };
    if (contentType.includes('text/event-stream')) {
      return { headers: res.headers, message: pickById(parseSseMessages(text), body.id) };
    }
    // application/json（或空 body 的 202）
    if (!text.trim()) return { headers: res.headers, message: null };
    let parsed;
    try {
      parsed = JSON.parse(text);
    } catch {
      throw new Error(`网关返回非 JSON 响应：${text.slice(0, 400)}`);
    }
    return { headers: res.headers, message: parsed };
  }

  async open() {
    const initId = this.nextId++;
    const { headers, message } = await this.post({
      jsonrpc: '2.0',
      id: initId,
      method: 'initialize',
      params: { protocolVersion: PROTOCOL_VERSION, capabilities: {}, clientInfo: CLIENT_INFO },
    });
    if (!message || message.error) {
      throw new Error(`initialize 失败：${message && message.error ? `${message.error.code}: ${message.error.message}` : '无响应'}`);
    }
    const result = message.result || {};
    // 会话 id 在 initialize 响应头 mcp-session-id（不在 result body 里）
    this.sessionId = headers.get('mcp-session-id') || result.sessionId || null;
    this.protocolVersion = result.protocolVersion || PROTOCOL_VERSION;
    this.serverInfo = result.serverInfo || null;
    await this.post({ jsonrpc: '2.0', method: 'notifications/initialized' }, { expectResponse: false }).catch(() => undefined);
  }

  async ensureOpen() {
    if (this.sessionId === null && this._opened !== true) {
      await this.open();
      this._opened = true;
    }
  }

  async reset() {
    this.sessionId = null;
    this._opened = false;
  }

  async close() {
    if (!this.sessionId) return;
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 3000);
      await fetch(this.config.url, {
        method: 'DELETE',
        headers: this.headers({ 'Mcp-Session-Id': this.sessionId }),
        signal: controller.signal,
      }).catch(() => undefined);
      clearTimeout(timer);
    } catch {
      // best-effort
    }
    this.sessionId = null;
    this._opened = false;
  }

  async request(method, params) {
    const id = this.nextId++;
    const { message } = await this.post({ jsonrpc: '2.0', id, method, params: params || {} });
    if (!message) throw new Error(`${method} 无响应`);
    if (message.error) throw new Error(`${method} JSON-RPC 错误：${message.error.code}: ${message.error.message}`);
    return message.result;
  }

  /** tools/call；带一次重建会话重试。 */
  async callTool(toolName, args) {
    const attempt = async () => {
      await this.ensureOpen();
      return this.request('tools/call', { name: toolName, arguments: args || {} });
    };
    let result;
    let firstError = null;
    try {
      result = await attempt();
    } catch (exc) {
      firstError = exc;
      await this.reset();
      try {
        result = await attempt();
      } catch (retryExc) {
        throw new ServiceError(`MCP Gateway 调用失败：tool=${toolName}`, {
          payload: {
            request: { gateway: this.config.url, method: 'tools/call', tool: toolName, arguments: args },
            error: retryExc instanceof Error ? `${retryExc.name}: ${retryExc.message}` : String(retryExc),
            first_error: firstError instanceof Error ? `${firstError.name}: ${firstError.message}` : String(firstError),
          },
        });
      }
    }
    return result;
  }
}

function parseSseMessages(text) {
  const dataChunks = [];
  let data = [];
  for (const line of text.split(/\r?\n/)) {
    if (line === '') {
      if (data.length) {
        dataChunks.push(data.join('\n'));
        data = [];
      }
      continue;
    }
    if (line.startsWith(':')) continue;
    if (line.startsWith('data:')) data.push(line.slice(5).replace(/^ /, ''));
  }
  if (data.length) dataChunks.push(data.join('\n'));
  const messages = [];
  for (const chunk of dataChunks) {
    try {
      messages.push(JSON.parse(chunk));
    } catch {
      // 跳过非 JSON data 帧
    }
  }
  return messages;
}

function pickById(messages, id) {
  if (id == null) return messages.length ? messages[messages.length - 1] : null;
  for (const message of messages) {
    if (message && message.id === id) return message;
  }
  return messages.length ? messages[messages.length - 1] : null;
}

/** 把 tools/call 结果解成业务对象：structuredContent 优先，否则拼 text 再 JSON.parse。 */
function parseToolText(result) {
  if (!result) return result;
  if (result.structuredContent !== undefined) return result.structuredContent;
  const texts = (result.content || [])
    .filter((item) => item && item.type === 'text' && typeof item.text === 'string')
    .map((item) => item.text);
  if (!texts.length) return result;
  const joined = texts.join('\n');
  try {
    return JSON.parse(joined);
  } catch {
    // 网关常把 JSON 嵌在说明文字末尾，尽量抽出最后一个 JSON 对象
    const match = joined.match(/\{[\s\S]*\}\s*$/);
    if (match) {
      try {
        return JSON.parse(match[0]);
      } catch {
        // fall through
      }
    }
    return { raw: joined };
  }
}

// ---------------------------------------------------------------------------
// UAP 文档路径 → 网关白名单工具映射（frontend-auth 文档口径）
// ---------------------------------------------------------------------------

const UAP_DOC_PATH_TO_GATEWAY = {
  '/resource/treeGrid': 'uap-api_tools_uap_resource_tree',
  '/resource/getButtonList': 'uap-api_tools_uap_resource_button_list',
  '/resource/add': 'uap-api_tools_uap_resource_add_menu',
  '/resource/addButton': 'uap-api_tools_uap_resource_add_button',
  '/resource/edit': 'uap-api_tools_uap_resource_edit',
  '/role/getUserRoleList': 'uap-api_tools_uap_role_user_roles',
  '/user/saveRole': 'uap-api_tools_uap_user_save_roles',
  '/role/getRoleResourceList': 'uap-api_tools_uap_role_resource_tree',
  '/role/addRoleRes': 'uap-api_tools_uap_role_save_resources',
};

function gatewayToolForDocPath(docPath) {
  const p = docPath.startsWith('/') ? docPath : `/${docPath}`;
  const name = UAP_DOC_PATH_TO_GATEWAY[p];
  if (!name) throw new ServiceError(`未映射到网关工具：${docPath}`);
  return name;
}

function asGatewayArgs(data) {
  const out = {};
  for (const [key, value] of Object.entries(data)) {
    if (value === undefined) continue;
    out[key] = value;
  }
  return out;
}

function pairsToArgs(pairs) {
  const singles = {};
  const multi = {};
  for (const [key, value] of pairs) {
    if (multi[key]) {
      multi[key].push(value);
      continue;
    }
    if (Object.prototype.hasOwnProperty.call(singles, key)) {
      multi[key] = [singles[key], value];
      delete singles[key];
      continue;
    }
    singles[key] = value;
  }
  const out = { ...singles };
  for (const [key, values] of Object.entries(multi)) {
    out[key] = values.join(',');
  }
  return out;
}

function toGatewayArgs(docPath, body) {
  let args;
  if (Array.isArray(body)) args = pairsToArgs(body);
  else if (body && typeof body === 'object') args = asGatewayArgs(body);
  else args = {};
  if (docPath === '/role/getUserRoleList' && args.externalUser === undefined) {
    args.externalUser = false;
  }
  return args;
}

/** 按文档路径调用 UAP：{ http_status, request, data }。 */
async function callUap(client, docPath, options) {
  let toolName;
  try {
    toolName = gatewayToolForDocPath(docPath);
  } catch (exc) {
    throw new ServiceError(exc instanceof Error ? exc.message : String(exc));
  }
  const args = toGatewayArgs(docPath, options?.body);
  const result = await client.callTool(toolName, args);
  const data = parseToolText(result);
  const out = {
    http_status: result && result.isError ? 502 : 200,
    request: { gateway: client.config.url, method: 'tools/call', tool: toolName, arguments: args },
    data,
  };
  if (result && result.isError) {
    throw new ServiceError(`MCP Gateway 工具返回错误：tool=${toolName}`, { payload: out });
  }
  return out;
}

// ---------------------------------------------------------------------------
// shared / uap-result
// ---------------------------------------------------------------------------

function asRecord(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  return value;
}

function asArray(value) {
  if (Array.isArray(value)) return value;
  const rec = asRecord(value);
  if (!rec) return [];
  for (const key of ['data', 'rows', 'list', 'records', 'trees', 'children']) {
    if (Array.isArray(rec[key])) return rec[key];
  }
  return [];
}

function toId(value) {
  if (value == null) return '';
  return String(value);
}

function unwrapUapData(result, label) {
  const httpStatus = Number(result.http_status ?? 0);
  if (httpStatus >= 400) {
    throw new ServiceError(`${label} HTTP ${httpStatus}`, { payload: result.data });
  }
  const body = result.data;
  const rec = asRecord(body);
  if (!rec) return body;
  const code = rec.code;
  const message = rec.message == null ? '' : String(rec.message);
  if (code === -11 || message.includes('非网关')) {
    throw new ServiceError(`${label} 当前环境可能禁止非网关直连（code=-11）`, { payload: body });
  }
  if (code === -2 || message.includes('未登录')) {
    throw new ServiceError(`${label} 接口可能需要登录态`, { payload: body });
  }
  if (code != null && code !== 1 && code !== 200 && String(code) !== '1') {
    throw new ServiceError(`${label} 失败：${message || `code=${String(code)}`}`, { payload: body });
  }
  return rec.data !== undefined ? rec.data : body;
}

function extractCreatedId(result) {
  const body = result.data;
  if (typeof body === 'number' || (typeof body === 'string' && body.trim() !== '')) {
    return String(body);
  }
  const rec = asRecord(body);
  if (!rec) return undefined;
  if (rec.id != null && String(rec.id).trim() !== '') return String(rec.id);
  const inner = rec.data;
  if (typeof inner === 'number' || (typeof inner === 'string' && inner.trim() !== '')) {
    return String(inner);
  }
  const innerRec = asRecord(inner);
  if (innerRec && innerRec.id != null && String(innerRec.id).trim() !== '') return String(innerRec.id);
  return undefined;
}

// ---------------------------------------------------------------------------
// domain / tree
// ---------------------------------------------------------------------------

function strField(raw, keys) {
  for (const key of keys) {
    const value = raw[key];
    if (value != null && String(value).trim() !== '') return String(value);
  }
  return undefined;
}

function numField(raw, keys) {
  for (const key of keys) {
    const value = raw[key];
    if (typeof value === 'number' && Number.isFinite(value)) return value;
    if (typeof value === 'string' && value.trim() !== '' && Number.isFinite(Number(value))) return Number(value);
  }
  return undefined;
}

function isFunctionGroupId(id) {
  return id.endsWith('function');
}

function isButtonGroupId(id) {
  return id.endsWith('button') && !id.endsWith('function');
}

function isGroupId(id) {
  return isFunctionGroupId(id) || isButtonGroupId(id);
}

function detectKind(raw, id, parentId) {
  if (isFunctionGroupId(id) || strField(raw, ['title', 'resName', 'name', 'text', 'label']) === '功能列表') return 'group';
  if (isButtonGroupId(id) || strField(raw, ['title', 'resName', 'name', 'text', 'label']) === '按钮列表') return 'group';
  if (parentId && isFunctionGroupId(parentId)) return 'function';
  if (parentId && isButtonGroupId(parentId)) return 'button';
  const resType = strField(raw, ['resType', 'type']);
  if (resType === '5') return 'function';
  if (resType === '4') return 'button';
  return 'menu';
}

function effectiveResType(node) {
  if (node.resType) return node.resType;
  if (node.kind === 'function') return '5';
  if (node.kind === 'button') return '4';
  if (node.kind === 'menu') return '1';
  return '';
}

/** 权限树里功能点/按钮的 parentResId 常为 `{页面菜单id}function|button`；Agent 只应传页面菜单 id。 */
function pageMenuIdFromParent(parentId) {
  if (!parentId) return undefined;
  if (isFunctionGroupId(parentId)) return parentId.slice(0, -'function'.length);
  if (isButtonGroupId(parentId)) return parentId.slice(0, -'button'.length);
  return parentId;
}

function parseNode(input, parentId) {
  const raw = asRecord(input);
  if (!raw) return null;
  const id = toId(raw.id ?? raw.key ?? raw.resId ?? raw.value);
  if (!id) return null;
  const name = strField(raw, ['resName', 'title', 'name', 'text', 'label']) || id;
  const childrenRaw = asArray(raw.children);
  const kind = detectKind(raw, id, parentId);
  const resType = strField(raw, ['resType', 'type']);
  const node = {
    id,
    name,
    resType: resType ?? (kind === 'function' ? '5' : kind === 'button' ? '4' : kind === 'menu' ? '1' : undefined),
    resUrl: strField(raw, ['resUrl', 'url', 'path']),
    resCode: strField(raw, ['resCode', 'code']),
    parentResId: strField(raw, ['parentResId', 'parentId']) ?? parentId,
    order: numField(raw, ['order', 'sort', 'seq']),
    kind,
    children: [],
    raw,
  };
  node.children = childrenRaw.map((child) => parseNode(child, id)).filter((child) => child != null);
  return node;
}

function parseForest(payload) {
  return asArray(payload).map((item) => parseNode(item)).filter((item) => item != null);
}

function flattenTree(nodes, ancestors = []) {
  const out = [];
  for (const node of nodes) {
    const ancestorPath = [...ancestors, node.name].join(' / ');
    out.push({ ...node, ancestorPath });
    if (node.children.length) out.push(...flattenTree(node.children, [...ancestors, node.name]));
  }
  return out;
}

function findNodeById(nodes, id) {
  const target = String(id);
  for (const node of nodes) {
    if (node.id === target) return node;
    const nested = findNodeById(node.children, target);
    if (nested) return nested;
  }
  return null;
}

function collectDescendantIds(node) {
  const ids = [node.id];
  for (const child of node.children) ids.push(...collectDescendantIds(child));
  return ids;
}

function findPageMenu(nodes, fromId) {
  const node = findNodeById(nodes, fromId);
  if (!node) return null;
  if (node.kind === 'menu' && !isGroupId(node.id)) return node;
  if (!node.parentResId) return null;
  return findPageMenu(nodes, node.parentResId);
}

function siblingMaxOrder(nodes, parentResId) {
  const parentKey = parentResId == null || parentResId === '' ? '0' : String(parentResId);
  const siblings = parentKey === '0' ? nodes : findNodeById(nodes, parentKey)?.children ?? [];
  let max = 0;
  for (const sib of siblings) {
    if (typeof sib.order === 'number' && sib.order > max) max = sib.order;
  }
  return max;
}

const SIMILAR_LIMIT = 8;

/** 精确名未命中时给出相近菜单，供用户确认（如「系统配置」→「系统设置」）。 */
function similarByName(nodes, name, limit = SIMILAR_LIMIT) {
  const needle = name.trim();
  if (!needle) return [];
  const flat = flattenTree(nodes, []).filter((node) => node.kind === 'menu');
  const scored = [];
  for (const node of flat) {
    if (node.name === needle) continue;
    let score = 0;
    if (node.name.includes(needle) || needle.includes(node.name)) {
      score = 100 + Math.min(node.name.length, needle.length);
    } else {
      let prefix = 0;
      const max = Math.min(needle.length, node.name.length);
      while (prefix < max && needle[prefix] === node.name[prefix]) prefix += 1;
      if (prefix >= 2) score = prefix * 10;
      const head = needle.slice(0, 2);
      if (head.length === 2 && node.name.includes(head)) score = Math.max(score, 20);
    }
    if (score > 0) scored.push({ score, hit: toHit(node) });
  }
  scored.sort((a, b) => b.score - a.score || a.hit.id.localeCompare(b.hit.id));
  const seen = new Set();
  const out = [];
  for (const item of scored) {
    if (seen.has(item.hit.id)) continue;
    seen.add(item.hit.id);
    out.push(item.hit);
    if (out.length >= limit) break;
  }
  return out;
}

function toHit(node) {
  return {
    id: node.id,
    resName: node.name,
    resType: node.resType ?? (node.kind === 'function' ? '5' : node.kind === 'button' ? '4' : '1'),
    kind: node.kind,
    parentResId: node.parentResId,
    resUrl: node.resUrl,
    resCode: node.resCode,
    ancestorPath: node.ancestorPath ?? node.name,
  };
}

function matchNode(node, query) {
  if (query.id && node.id !== String(query.id)) return false;
  if (query.resType && effectiveResType(node) !== query.resType) {
    if (!(query.resType === '1' && node.kind === 'menu')) return false;
  }
  if (query.resName && node.name !== query.resName) return false;
  if (query.resUrl && (node.resUrl ?? '') !== query.resUrl) return false;
  if (query.resCode && (node.resCode ?? '') !== query.resCode) return false;
  return Boolean(query.id || query.resName || query.resUrl || query.resCode || query.resType);
}

function parseButtonList(payload, parentResId) {
  return asArray(payload)
    .map((item) => {
      const node = parseNode(item, parentResId);
      if (!node) return null;
      if (!node.resType) {
        node.resType = node.kind === 'button' ? '4' : '5';
        node.kind = node.resType === '4' ? 'button' : 'function';
      }
      return node;
    })
    .filter((item) => item != null);
}

// ---------------------------------------------------------------------------
// domain / application（应用快照：data[].value = appId，data[].label = uapName）
// ---------------------------------------------------------------------------

function resolveDataFile() {
  const candidates = [
    process.env.UAP_APPLICATION_ALL,
    path.join(SCRIPT_DIR, 'data', 'application-all.json'),
    path.join(process.cwd(), 'data', 'application-all.json'),
  ].filter(Boolean);
  for (const file of candidates) {
    if (fs.existsSync(file)) return file;
  }
  throw new ServiceError(`未找到 data/application-all.json（已尝试：${candidates.join(' ; ')}）。请放入 /application/all 接口完整返回（快照机制：无鉴权直连常返回空 data）`);
}

function loadApplicationAll() {
  const file = resolveDataFile();
  let data;
  try {
    data = JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (exc) {
    throw new ServiceError(`读取 application-all.json 失败：${exc instanceof Error ? exc.message : String(exc)}`);
  }
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    throw new ServiceError('application-all.json 须为接口完整返回对象（含 code/data 等）');
  }
  if (!Array.isArray(data.data)) {
    throw new ServiceError('application-all.json.data 须为数组');
  }
  return { http_status: 200, request: { source: 'local-file', path: file }, data };
}

function itemsFromApplicationAll(payload) {
  const body = asRecord(payload.data) ?? asRecord(payload);
  const rows = asArray(body?.data ?? body);
  const items = [];
  for (const row of rows) {
    const rec = asRecord(row);
    if (!rec) continue;
    const value = rec.value == null ? '' : String(rec.value);
    const label = rec.label == null ? '' : String(rec.label);
    if (!value && !label) continue;
    items.push({ value, label });
  }
  return items;
}

function resolveApplication(items, uapName) {
  const name = uapName.trim();
  const exact = items.filter((item) => item.label === name);
  if (exact.length === 1) return { matched: true, appId: exact[0].value, uapName: exact[0].label };
  if (exact.length > 1) {
    return {
      matched: false,
      uapName: name,
      message: `uapName「${name}」匹配到多个应用，请核对`,
      similar: exact.map((item) => `${item.label} (${item.value})`).slice(0, SIMILAR_LIMIT),
    };
  }
  const similar = items
    .filter((item) => item.label.includes(name) || name.includes(item.label))
    .slice(0, SIMILAR_LIMIT)
    .map((item) => item.label);
  return {
    matched: false,
    uapName: name,
    message: `未找到 label === 「${name}」的应用，请核对 rules-config.yaml 的 uapName`,
    similar,
  };
}

// ---------------------------------------------------------------------------
// domain / resource-merge（编辑合并：现有记录 + 变更字段 → 全量写回）
// ---------------------------------------------------------------------------

const MENU_FIELDS = ['id', 'appId', 'resName', 'resUrl', 'resType', 'parentResId', 'status', 'visible', 'accountLine', 'order', 'single', 'domain', 'contractUrl', 'iframeUrl', 'resDesc', 'imagePath'];
const FUNCTION_FIELDS = ['id', 'appId', 'parentResId', 'resName', 'resCode', 'resType', 'status', 'accountLine', 'buttonUrls', 'interfaceUrls', 'function'];
const BUTTON_FIELDS = ['id', 'appId', 'parentResId', 'resName', 'resCode', 'resType', 'status', 'accountLine'];

function pickRaw(raw, keys) {
  const out = {};
  for (const key of keys) {
    if (raw[key] !== undefined) out[key] = raw[key];
  }
  return out;
}

function overlay(base, patch, keys) {
  const out = { ...base };
  for (const key of keys) {
    if (patch[key] !== undefined) out[key] = patch[key];
  }
  return out;
}

function mergeFunctionPayload(current, patch) {
  const cur = current && typeof current === 'object' && !Array.isArray(current) ? { ...current } : {};
  if (patch == null) return Object.keys(cur).length ? cur : current;
  if (typeof patch !== 'object' || Array.isArray(patch)) return patch;
  const out = { ...cur };
  if (patch.actions !== undefined && patch.actions !== null) out.actions = patch.actions;
  if (patch.interfaces !== undefined && patch.interfaces !== null) out.interfaces = patch.interfaces;
  return out;
}

function mergeMenuEdit(node, patch, appId) {
  const base = pickRaw(node.raw, MENU_FIELDS);
  base.id = node.id;
  base.appId = appId;
  base.resName = patch.resName ?? base.resName ?? node.name;
  base.resUrl = patch.resUrl ?? base.resUrl ?? node.resUrl ?? '';
  base.resType = '1';
  base.parentResId = patch.parentResId !== undefined ? patch.parentResId : base.parentResId ?? node.parentResId ?? null;
  if (base.status === undefined) base.status = 1;
  if (base.visible === undefined) base.visible = 1;
  if (base.accountLine === undefined) base.accountLine = 1;
  if (base.order === undefined) base.order = node.order ?? 1;
  if (base.single === undefined) base.single = 0;
  for (const key of ['domain', 'contractUrl', 'iframeUrl', 'resDesc', 'imagePath']) {
    if (base[key] === undefined) base[key] = '';
  }
  const merged = overlay(base, patch, MENU_FIELDS);
  merged.resType = '1';
  merged.appId = appId;
  merged.id = node.id;
  return merged;
}

function mergeFunctionEdit(node, patch, appId) {
  const base = pickRaw(node.raw, FUNCTION_FIELDS);
  base.id = node.id;
  base.appId = appId;
  base.parentResId = patch.parentResId ?? base.parentResId ?? node.parentResId;
  base.resName = patch.resName ?? base.resName ?? node.name;
  base.resCode = patch.resCode ?? base.resCode ?? node.resCode ?? '';
  base.resType = '5';
  if (base.status === undefined) base.status = 1;
  if (base.accountLine === undefined) base.accountLine = 1;
  if (base.buttonUrls === undefined) base.buttonUrls = '';
  if (base.interfaceUrls === undefined) base.interfaceUrls = '';
  const merged = overlay(base, patch, FUNCTION_FIELDS);
  merged.function = mergeFunctionPayload(base.function, patch.function);
  merged.resType = '5';
  merged.appId = appId;
  merged.id = node.id;
  if (merged.parentResId == null || merged.parentResId === '') {
    throw new ServiceError('编辑功能点须提供 parentResId（页面菜单 id）');
  }
  return merged;
}

function mergeButtonEdit(node, patch, appId) {
  const base = pickRaw(node.raw, BUTTON_FIELDS);
  base.id = node.id;
  base.appId = appId;
  base.parentResId = patch.parentResId ?? base.parentResId ?? node.parentResId;
  base.resName = patch.resName ?? base.resName ?? node.name;
  base.resCode = patch.resCode ?? base.resCode ?? node.resCode ?? '';
  base.resType = '4';
  if (base.status === undefined) base.status = 1;
  if (base.accountLine === undefined) base.accountLine = 1;
  const merged = overlay(base, patch, BUTTON_FIELDS);
  merged.resType = '4';
  merged.appId = appId;
  merged.id = node.id;
  if (merged.parentResId == null || merged.parentResId === '') {
    throw new ServiceError('编辑旧按钮权限须提供 parentResId（页面菜单 id）');
  }
  return merged;
}

// ---------------------------------------------------------------------------
// domain / user-roles
// ---------------------------------------------------------------------------

function parseUserRoleState(payload) {
  const rec = asRecord(payload) ?? {};
  const roleListRaw = asArray(rec.roleList ?? rec.rows);
  const roleList = roleListRaw.map((item) => {
    const row = asRecord(item) ?? {};
    const roleId = toId(row.roleId ?? row.id ?? row.value);
    const roleName = String(row.roleName ?? row.name ?? row.label ?? roleId);
    const choose = Boolean(row.choose) || row.choose === 1;
    return { roleId, roleName, choose };
  });
  const selectedFromKeys = asArray(rec.selectedRowKeys).map((item) => toId(item)).filter(Boolean);
  const selectedFromChoose = roleList.filter((row) => row.choose).map((row) => row.roleId);
  const selectedRowKeys = selectedFromKeys.length ? selectedFromKeys : selectedFromChoose;
  return { selectedRowKeys, roleList };
}

function similarRoleNames(roleList, name, limit = 8) {
  const needle = name.trim();
  if (!needle) return [];
  const scored = [];
  for (const row of roleList) {
    if (row.roleName === needle) continue;
    let score = 0;
    if (row.roleName.includes(needle) || needle.includes(row.roleName)) {
      score = 100 + Math.min(row.roleName.length, needle.length);
    } else {
      let prefix = 0;
      const max = Math.min(needle.length, row.roleName.length);
      while (prefix < max && needle[prefix] === row.roleName[prefix]) prefix += 1;
      if (prefix >= 2) score = prefix * 10;
      const head = needle.slice(0, 2);
      if (head.length === 2 && row.roleName.includes(head)) score = Math.max(score, 20);
    }
    if (score > 0) scored.push({ score, roleId: row.roleId, roleName: row.roleName });
  }
  scored.sort((a, b) => b.score - a.score || a.roleId.localeCompare(b.roleId));
  return scored.slice(0, limit).map(({ roleId, roleName }) => ({ roleId, roleName }));
}

function compactUserRoleState(state, uId, query) {
  const selectedRoles = state.roleList
    .filter((row) => state.selectedRowKeys.includes(row.roleId))
    .map((row) => ({ roleId: row.roleId, roleName: row.roleName, choose: true }));
  const adminRoles = state.roleList
    .filter((row) => row.roleName === 'admin')
    .map((row) => ({ roleId: row.roleId, roleName: row.roleName, choose: state.selectedRowKeys.includes(row.roleId) }));
  const queried = query?.roleName != null && query.roleName !== ''
    ? state.roleList
        .filter((row) => row.roleName === query.roleName)
        .map((row) => ({ roleId: row.roleId, roleName: row.roleName, choose: state.selectedRowKeys.includes(row.roleId) }))
    : undefined;
  const queriedMiss = query?.roleName != null && query.roleName !== '' && (!queried || queried.length === 0);
  return {
    uId,
    selectedRowKeys: state.selectedRowKeys,
    selectedRoles,
    roleCount: state.roleList.length,
    adminRoleExists: adminRoles.length > 0,
    adminRoles: adminRoles.length ? adminRoles : undefined,
    queriedRoles: queried,
    similarRoles: queriedMiss ? similarRoleNames(state.roleList, query?.roleName ?? '') : undefined,
    hint: adminRoles.length
      ? undefined
      : '应用下没有名为 admin 的角色。请向用户展示 selectedRoles（已绑角色）供确认；禁止把全量角色名贴进对话。核对其它角色名时再次调用并传入 roleName。',
  };
}

function resolveRoleIds(state, names, ids, label) {
  const out = [];
  for (const id of ids ?? []) {
    const sid = String(id);
    const found = state.roleList.find((row) => row.roleId === sid);
    if (!found) {
      throw new ServiceError(`${label}角色 id「${sid}」不存在`, {
        payload: { roleCount: state.roleList.length, hint: '禁止把全量角色名贴进对话。请改用已绑角色 id 或 roleName。' },
      });
    }
    out.push(sid);
  }
  for (const name of names ?? []) {
    const matches = state.roleList.filter((row) => row.roleName === name);
    if (matches.length === 0) {
      throw new ServiceError(`${label}角色名「${name}」不存在`, {
        payload: {
          similarRoles: similarRoleNames(state.roleList, name),
          roleCount: state.roleList.length,
          hint: '禁止把全量角色名贴进对话。请向用户展示已绑角色，或用 get-user-roles 传入 role-name 再查。',
        },
      });
    }
    if (matches.length > 1) {
      throw new ServiceError(`${label}角色名「${name}」匹配到多个角色，请改用 roleId`, { payload: { candidates: matches } });
    }
    out.push(matches[0].roleId);
  }
  return out;
}

function mergeUserRoles(state, intent) {
  const addIds = resolveRoleIds(state, intent.addRoleNames, intent.addRoleIds, '拟新增');
  const removeIds = new Set(resolveRoleIds(state, intent.removeRoleNames, intent.removeRoleIds, '拟移除'));
  const before = [...state.selectedRowKeys];
  const afterSet = new Set(before);
  for (const id of addIds) afterSet.add(id);
  for (const id of removeIds) afterSet.delete(id);
  const after = [...afterSet];
  const added = after
    .filter((id) => !before.includes(id))
    .map((id) => state.roleList.find((row) => row.roleId === id))
    .filter(Boolean);
  const removed = before
    .filter((id) => !after.includes(id))
    .map((id) => state.roleList.find((row) => row.roleId === id))
    .filter(Boolean);
  return { before, after, added, removed };
}

// ---------------------------------------------------------------------------
// domain / role-keys（角色权限 keys 解析与祖先勾选重算）
// ---------------------------------------------------------------------------

function parseRoleResourceState(payload) {
  const rec = asRecord(payload);
  const trees = parseForest(rec ? rec.trees ?? rec.rows ?? rec.data ?? payload : payload);
  const checkedKeys = asArray(rec?.checkedKeys).map((item) => toId(item)).filter(Boolean);
  const halfCheckedKeys = asArray(rec?.halfCheckedKeys).map((item) => toId(item)).filter(Boolean);
  return { trees, checkedKeys, halfCheckedKeys };
}

function parentResIdMatches(node, want) {
  const direct = node.parentResId ?? '';
  const pageId = pageMenuIdFromParent(node.parentResId);
  const wantPage = pageMenuIdFromParent(want) ?? want;
  return direct === want || pageId === want || pageId === wantPage || direct === wantPage;
}

function nodeMatchesRef(node, ref) {
  if (ref.id != null && node.id !== String(ref.id)) return false;
  // id 已唯一命中时不再因 resType 不一致失败（权限树节点常缺 resType）
  if (ref.id == null && ref.resType && effectiveResType(node) !== ref.resType) {
    if (!(ref.resType === '1' && node.kind === 'menu')) return false;
  }
  if (ref.resName && node.name !== ref.resName) return false;
  if (ref.resUrl && (node.resUrl ?? '') !== ref.resUrl) return false;
  if (ref.resCode && (node.resCode ?? '') !== ref.resCode) return false;
  if (ref.parentResId != null && !parentResIdMatches(node, String(ref.parentResId))) return false;
  return Boolean(ref.id != null || ref.resName || ref.resUrl || ref.resCode);
}

function resolveResourceRefs(trees, refs, label) {
  const flat = [];
  const walk = (nodes) => {
    for (const node of nodes) {
      flat.push(node);
      if (node.children.length) walk(node.children);
    }
  };
  walk(trees);
  const resolved = [];
  for (const ref of refs) {
    const byId = ref.id != null ? flat.filter((node) => node.kind !== 'group' && node.id === String(ref.id)) : [];
    // 权限树 id 全局唯一：命中则采用，忽略 resType / 分组父级写法
    const hits = byId.length === 1 ? byId : flat.filter((node) => node.kind !== 'group' && nodeMatchesRef(node, ref));
    if (hits.length === 0) {
      const named = ref.resName
        ? flat
            .filter((node) => node.kind !== 'group' && node.name === ref.resName)
            .slice(0, 8)
            .map((node) => ({
              id: node.id,
              resName: node.name,
              resType: effectiveResType(node),
              parentResId: pageMenuIdFromParent(node.parentResId) ?? node.parentResId,
            }))
        : [];
      throw new ServiceError(`${label}未找到资源：${JSON.stringify(ref)}`, {
        payload: { ref, candidates: named, hint: '功能点 parentResId 请传页面菜单 id，不要传 `{菜单id}function`。若仍失败，改用 id。' },
      });
    }
    if (hits.length > 1) {
      throw new ServiceError(`${label}资源匹配到多条，请改用 id 或补 parentResId / resType`, {
        payload: {
          ref,
          candidates: hits.slice(0, 10).map((node) => ({
            id: node.id,
            resName: node.name,
            resType: effectiveResType(node),
            parentResId: pageMenuIdFromParent(node.parentResId) ?? node.parentResId,
          })),
        },
      });
    }
    resolved.push(hits[0]);
  }
  return resolved;
}

function isMenuLike(node) {
  return node.kind === 'menu' && !isGroupId(node.id);
}

function recomputeKeys(trees, granted) {
  const checked = new Set(granted);
  const half = new Set();
  const applyParentState = (node, kids) => {
    if (!kids.length) return;
    const all = kids.every((child) => checked.has(child.id));
    const some = kids.some((child) => checked.has(child.id) || half.has(child.id));
    if (all) {
      checked.add(node.id);
      half.delete(node.id);
    } else if (some) {
      half.add(node.id);
      checked.delete(node.id);
    } else {
      checked.delete(node.id);
      half.delete(node.id);
    }
  };
  const walk = (node) => {
    for (const child of node.children) walk(child);
    if (isFunctionGroupId(node.id) || isButtonGroupId(node.id) || node.kind === 'group') {
      applyParentState(node, node.children);
      return;
    }
    const menuKids = node.children.filter(isMenuLike);
    if (menuKids.length > 0) applyParentState(node, menuKids);
  };
  for (const root of trees) walk(root);
  for (const id of [...checked]) {
    if (half.has(id)) half.delete(id);
  }
  return { checkedKeys: [...checked], halfCheckedKeys: [...half] };
}

function applyRoleResourceIntent(state, addNodes, removeNodes) {
  const granted = new Set(state.checkedKeys.filter((id) => !isGroupId(id)));
  for (const node of removeNodes) {
    for (const id of collectDescendantIds(node)) granted.delete(id);
  }
  const addedMeta = [];
  for (const node of addNodes) {
    if (!granted.has(node.id)) addedMeta.push({ id: node.id, resName: node.name, resType: node.resType });
    granted.add(node.id);
    const page = findPageMenu(state.trees, node.id);
    if (page && !granted.has(page.id)) addedMeta.push({ id: page.id, resName: page.name, resType: page.resType });
    if (page) granted.add(page.id);
  }
  const next = recomputeKeys(state.trees, granted);
  const removed = removeNodes.map((node) => ({ id: node.id, resName: node.name, resType: node.resType }));
  return { checkedKeys: next.checkedKeys, halfCheckedKeys: next.halfCheckedKeys, added: addedMeta, removed };
}

function sameKeySet(a, b) {
  if (a.length !== b.length) return false;
  const sb = new Set(b);
  return a.every((item) => sb.has(item));
}

function findRoleIdByName(roleList, roleName) {
  const matches = roleList.filter((row) => row.roleName === roleName);
  if (matches.length === 1) return matches[0].roleId;
  if (matches.length === 0) {
    throw new ServiceError(`角色名「${roleName}」不存在`, {
      payload: {
        roleCount: roleList.length,
        similarRoles: similarRoleNames(roleList, roleName),
        hint: '禁止把全量角色名贴进对话。请向用户展示 get-user-roles 的 selectedRoles，或传入 roleName 再查。',
      },
    });
  }
  throw new ServiceError(`角色名「${roleName}」匹配到多个，请改用 roleId`);
}

// ---------------------------------------------------------------------------
// ops / uap-fetch
// ---------------------------------------------------------------------------

function slimWrite(result, extra) {
  const body = result.data;
  const rec = body && typeof body === 'object' && !Array.isArray(body) ? body : { data: body };
  return {
    http_status: result.http_status,
    code: rec.code,
    message: rec.message,
    data: rec.data !== undefined ? rec.data : body,
    ...(extra || {}),
  };
}

function formFromObject(data) {
  const out = {};
  for (const [key, value] of Object.entries(data)) {
    if (value === undefined) continue;
    out[key] = value == null ? '' : String(value);
  }
  return out;
}

function repeatedForm(base, checkedKeys, halfCheckedKeys) {
  const items = Object.entries(base);
  for (const key of checkedKeys) items.push(['checkedKeys', key]);
  for (const key of halfCheckedKeys) items.push(['halfCheckedKeys', key]);
  return items;
}

async function loadMenuForest(client, appId) {
  const result = await callUap(client, '/resource/treeGrid', { body: { appId } });
  return parseForest(unwrapUapData(result, 'resource/treeGrid'));
}

async function loadButtonList(client, appId, parentResId, resType) {
  const result = await callUap(client, '/resource/getButtonList', {
    body: { appId, resId: String(parentResId), resType },
  });
  return parseButtonList(unwrapUapData(result, 'resource/getButtonList'), String(parentResId));
}

async function loadUserRoles(client, appId, uId) {
  const result = await callUap(client, '/role/getUserRoleList', { body: { appId, uId } });
  return parseUserRoleState(unwrapUapData(result, 'role/getUserRoleList'));
}

async function loadRoleResources(client, appId, roleId) {
  const result = await callUap(client, '/role/getRoleResourceList', {
    body: { appId, roleId, resType: '4' },
  });
  return parseRoleResourceState(unwrapUapData(result, 'role/getRoleResourceList'));
}

// ---------------------------------------------------------------------------
// ops / resource
// ---------------------------------------------------------------------------

const LOOKUP_LIMIT = 20;

function filterHits(nodes, query, options) {
  const flat = flattenTree(nodes, []);
  const q = {
    id: query.id == null ? undefined : String(query.id),
    resName: query.resName,
    resUrl: query.resUrl,
    resCode: query.resCode,
    resType: query.resType,
  };
  const hasMatcher = Boolean(q.id || q.resName || q.resUrl || q.resCode);
  return flat
    .filter((node) => (hasMatcher ? matchNode(node, q) : true))
    .filter((node) => node.kind !== 'group')
    .filter((node) => {
      if (options?.directParentId == null) return true;
      return (node.parentResId ?? '') === options.directParentId;
    })
    .map(toHit);
}

function resolveParent(menus, input) {
  if (input.parentResId != null) {
    const node = findNodeById(menus, String(input.parentResId));
    if (!node || node.kind !== 'menu') {
      return { ok: false, similarParents: [], hint: `未找到父目录 id=${String(input.parentResId)}。禁止改用其它位置的同名页面。` };
    }
    return { ok: true, id: node.id, hit: toHit(node) };
  }
  if (!input.parentResName) return undefined;
  const hits = filterHits(menus, { appId: input.appId, resName: input.parentResName, resType: '1' });
  if (hits.length === 1) return { ok: true, id: hits[0].id, hit: hits[0] };
  if (hits.length > 1) {
    return {
      ok: false,
      similarParents: hits.slice(0, 10),
      hint: `父目录「${input.parentResName}」匹配到多条，请让用户确认后改用 parentResId。禁止擅自挑第一条，禁止改用其它位置的同名页面。`,
    };
  }
  return {
    ok: false,
    similarParents: similarByName(menus, input.parentResName),
    hint:
      `未找到父目录「${input.parentResName}」。须把 similarParents 列给用户确认真实目录名；` +
      `禁止把该名称理解成「去 UAP 里配置」而丢掉父目录；禁止改用其它位置的同名页面。`,
  };
}

function packLookup(input) {
  return {
    matched: input.matched,
    existsUnderParent: input.existsUnderParent,
    scope: input.scope,
    parentMatched: input.parentMatched,
    parent: input.parent,
    similarParents: input.similarParents?.length ? input.similarParents.slice(0, LOOKUP_LIMIT) : undefined,
    hint: input.hint,
    truncated: input.matches.length > LOOKUP_LIMIT,
    total: input.matches.length,
    matches: input.matches.slice(0, LOOKUP_LIMIT),
  };
}

async function resourceLookup(client, input) {
  if (
    input.id == null &&
    !input.resName &&
    !input.resUrl &&
    !input.resCode &&
    input.parentResId == null &&
    !input.parentResName
  ) {
    throw new ServiceError('至少提供 id / resName / resUrl / resCode / parentResId / parentResName 之一，禁止拉整棵资源树');
  }
  const menus = await loadMenuForest(client, input.appId);
  const parent = resolveParent(menus, input);
  if (parent && parent.ok === false) {
    return packLookup({
      matched: false,
      matches: [],
      scope: 'parent',
      existsUnderParent: false,
      parentMatched: false,
      similarParents: parent.similarParents,
      hint: parent.hint,
    });
  }
  const parentId = parent?.ok ? parent.id : undefined;
  const explicitFunc = input.resType === '4' || input.resType === '5' || Boolean(input.resCode);
  const explicitMenu = input.resType === '1';
  const hasId = input.id != null;
  let menuHits = [];
  if (!explicitFunc) {
    menuHits = filterHits(menus, { ...input, resType: explicitMenu ? '1' : undefined }, parentId ? { directParentId: parentId } : undefined);
  }
  const funcHits = [];
  const needFuncs = explicitFunc || (hasId && menuHits.length === 0 && Boolean(parentId));
  if (needFuncs) {
    const pageIds = [];
    if (parentId) pageIds.push(parentId);
    else if (menuHits.length === 1) pageIds.push(menuHits[0].id);
    if (!pageIds.length) {
      if (hasId && !explicitFunc) {
        return packLookup({
          matched: false,
          matches: [],
          scope: 'global',
          existsUnderParent: null,
          hint:
            `未在菜单树找到 id=${String(input.id)}。若为功能点/按钮，请带 parentResId（页面菜单 id）与 resType "5"/"4"；` +
            '创建后优先使用 create-function / create-menu 返回的 created.id。',
        });
      }
      throw new ServiceError('查功能点/按钮须提供 parentResId（页面菜单 id），或先查到唯一页面菜单');
    }
    const types = input.resType === '4' || input.resType === '5' ? [input.resType] : ['5', '4'];
    for (const pageId of pageIds) {
      for (const resType of types) {
        const buttons = await loadButtonList(client, input.appId, pageId, resType);
        funcHits.push(...filterHits(buttons, { ...input, resType, parentResId: pageId }));
      }
    }
  }
  const resultHits = explicitFunc || (hasId && menuHits.length === 0) ? funcHits : menuHits;
  const scoped = Boolean(parentId);
  if (scoped && parent?.ok) {
    const existsUnderParent = resultHits.length > 0;
    return packLookup({
      matched: existsUnderParent,
      matches: resultHits,
      scope: 'parent',
      existsUnderParent,
      parentMatched: true,
      parent: { id: parent.hit.id, resName: parent.hit.resName, ancestorPath: parent.hit.ancestorPath },
      hint: existsUnderParent ? undefined : input.resName ? `「${parent.hit.resName}」下没有「${input.resName}」。须在该目录下 create-menu。` : undefined,
    });
  }
  const similar = !explicitFunc && input.resName && resultHits.length === 0 ? similarByName(menus, input.resName) : [];
  return packLookup({
    matched: resultHits.length > 0,
    matches: resultHits,
    scope: 'global',
    existsUnderParent: null,
    similarParents: similar.length ? similar : undefined,
    hint: !explicitFunc && input.resName
      ? '未限定父目录。若用户指定了「在某目录下创建」，禁止把本次 matches 当作该目录已存在；必须带 parentResName 再查。其它位置同名必须在指定目录下新建，禁止改用，禁止把改用问成默认项。'
      : undefined,
  });
}

async function resourceAdd(client, input) {
  const menus = await loadMenuForest(client, input.appId);
  const parentKey = input.parentResId == null ? '0' : String(input.parentResId);
  const siblings = parentKey === '0' ? menus : findNodeById(menus, parentKey)?.children ?? [];
  const dup = siblings.find((item) => item.name === input.resName);
  if (dup) {
    throw new ServiceError(`该目录下已有同名菜单「${input.resName}」（id=${dup.id}），勿重复创建`);
  }
  const payload = { ...input };
  if (payload.order == null) {
    payload.order = siblingMaxOrder(menus, parentKey) + 1;
  }
  const result = await callUap(client, '/resource/add', { body: formFromObject(payload) });
  unwrapUapData(result, 'resource/add');
  const menusAfter = await loadMenuForest(client, input.appId);
  const siblingsAfter = parentKey === '0' ? menusAfter : findNodeById(menusAfter, parentKey)?.children ?? [];
  const createdNode = siblingsAfter.find((item) => item.name === input.resName);
  const extractedId = extractCreatedId(result);
  const created = createdNode
    ? { id: createdNode.id, resName: createdNode.name, resUrl: createdNode.resUrl, parentResId: createdNode.parentResId, resType: '1' }
    : extractedId
      ? { id: extractedId, resName: input.resName, resUrl: input.resUrl, parentResId: input.parentResId == null ? undefined : String(input.parentResId), resType: '1' }
      : undefined;
  return slimWrite(result, { order: payload.order, created });
}

async function resourceAddButton(client, input) {
  const result = await callUap(client, '/resource/addButton', { body: input });
  unwrapUapData(result, 'resource/addButton');
  const buttons = await loadButtonList(client, input.appId, String(input.parentResId), '5');
  const createdNode = buttons.find((item) => item.name === input.resName) ?? buttons.find((item) => item.resCode === input.resCode);
  const extractedId = extractCreatedId(result);
  const created = createdNode
    ? { id: createdNode.id, resName: createdNode.name, resCode: createdNode.resCode, parentResId: String(input.parentResId), resType: '5' }
    : extractedId
      ? { id: extractedId, resName: input.resName, resCode: input.resCode, parentResId: String(input.parentResId), resType: '5' }
      : undefined;
  return slimWrite(result, { created });
}

async function resourceEditMenu(client, input) {
  const menus = await loadMenuForest(client, input.appId);
  const node = findNodeById(menus, String(input.id));
  if (!node || node.kind !== 'menu') {
    throw new ServiceError(`未找到菜单 id=${String(input.id)}`);
  }
  const merged = mergeMenuEdit(node, input, input.appId);
  const result = await callUap(client, '/resource/edit', { body: merged });
  unwrapUapData(result, 'resource/edit');
  return slimWrite(result, { mergedFields: Object.keys(merged) });
}

async function resourceEditFunction(client, input) {
  const buttons = await loadButtonList(client, input.appId, String(input.parentResId), '5');
  const node = buttons.find((item) => item.id === String(input.id));
  if (!node) {
    throw new ServiceError(`未找到功能点 id=${String(input.id)}（parentResId=${String(input.parentResId)}）`);
  }
  const merged = mergeFunctionEdit(node, input, input.appId);
  const result = await callUap(client, '/resource/edit', { body: merged });
  unwrapUapData(result, 'resource/edit');
  return slimWrite(result);
}

async function resourceEditButton(client, input) {
  const buttons = await loadButtonList(client, input.appId, String(input.parentResId), '4');
  const node = buttons.find((item) => item.id === String(input.id));
  if (!node) {
    throw new ServiceError(`未找到旧按钮权限 id=${String(input.id)}（parentResId=${String(input.parentResId)}）`);
  }
  const merged = mergeButtonEdit(node, input, input.appId);
  const result = await callUap(client, '/resource/edit', { body: merged });
  unwrapUapData(result, 'resource/edit');
  return slimWrite(result);
}

// ---------------------------------------------------------------------------
// ops / role
// ---------------------------------------------------------------------------

async function resolveRoleId(client, input) {
  if (input.roleId) return { roleId: input.roleId, roleName: input.roleName };
  if (!input.roleName) throw new ServiceError('须提供 roleId 或 roleName');
  const state = await loadUserRoles(client, input.appId, input.uId || '12436');
  const roleId = findRoleIdByName(state.roleList, input.roleName);
  return { roleId, roleName: input.roleName };
}

async function roleIntent(client, input, write) {
  const addRefs = input.add ?? [];
  const removeRefs = input.remove ?? [];
  if (!addRefs.length && !removeRefs.length) {
    throw new ServiceError('须提供 add 或 remove 至少一项');
  }
  const role = await resolveRoleId(client, input);
  const state = await loadRoleResources(client, input.appId, role.roleId);
  const addNodes = addRefs.length ? resolveResourceRefs(state.trees, addRefs, '拟新增') : [];
  const removeNodes = removeRefs.length ? resolveResourceRefs(state.trees, removeRefs, '拟移除') : [];
  const next = applyRoleResourceIntent(state, addNodes, removeNodes);
  const summary = {
    roleId: role.roleId,
    roleName: role.roleName,
    added: next.added,
    removed: next.removed,
    unchangedCount: next.checkedKeys.filter((id) => !next.added.some((item) => item.id === id) && !isGroupId(id)).length,
    checkedCount: next.checkedKeys.length,
    halfCheckedCount: next.halfCheckedKeys.length,
  };
  if (!write) return { preview: true, ...summary };
  const unchanged = sameKeySet(state.checkedKeys, next.checkedKeys) && sameKeySet(state.halfCheckedKeys, next.halfCheckedKeys);
  if (unchanged) return { saved: false, unchanged: true, ...summary };
  const result = await callUap(client, '/role/addRoleRes', {
    body: repeatedForm({ appId: input.appId, roleId: role.roleId }, next.checkedKeys, next.halfCheckedKeys),
  });
  unwrapUapData(result, 'role/addRoleRes');
  return { saved: true, ...summary };
}

async function roleGetUserRoleList(client, input) {
  const state = await loadUserRoles(client, input.appId, input.uId);
  return compactUserRoleState(state, input.uId, { roleName: input.roleName });
}

async function userSaveRole(client, input) {
  if (
    !(input.addRoleNames?.length || input.removeRoleNames?.length || input.addRoleIds?.length || input.removeRoleIds?.length)
  ) {
    throw new ServiceError('须提供 addRoleNames / removeRoleNames / addRoleIds / removeRoleIds 至少一项');
  }
  const state = await loadUserRoles(client, input.appId, input.uId);
  const merged = mergeUserRoles(state, input);
  const changed = merged.before.slice().sort().join(',') !== merged.after.slice().sort().join(',');
  if (!changed) {
    return { saved: false, unchanged: true, uId: input.uId, before: merged.before, after: merged.after, added: merged.added, removed: merged.removed };
  }
  const result = await callUap(client, '/user/saveRole', {
    body: { appId: input.appId, uId: input.uId, roleIds: merged.after.join(',') },
  });
  unwrapUapData(result, 'user/saveRole');
  return { saved: true, uId: input.uId, before: merged.before, after: merged.after, added: merged.added, removed: merged.removed };
}

// ---------------------------------------------------------------------------
// 入参 strict 校验（等价 zod .strict()；未知字段拒绝、必填校验、默认值回填）
// ---------------------------------------------------------------------------

function typeOf(value) {
  if (Array.isArray(value)) return 'array';
  if (value === null) return 'null';
  return typeof value;
}

function checkField(label, name, spec, value, errorsOut) {
  if (value === undefined) return;
  if (value === null) {
    if (!spec.nullable) errorsOut.push(`${label}.${name} 不接受 null`);
    return;
  }
  const actual = typeOf(value);
  const acceptable = spec.union ? spec.union : [spec.type];
  if (!acceptable.includes(actual)) {
    errorsOut.push(`${label}.${name} 须为 ${acceptable.join('|')}，实际 ${actual}`);
    return;
  }
  if (spec.type === 'number' && !Number.isFinite(value)) {
    errorsOut.push(`${label}.${name} 须为有限数字`);
    return;
  }
  if (spec.enumValues && !spec.enumValues.includes(value)) {
    errorsOut.push(`${label}.${name} 须为 ${JSON.stringify(spec.enumValues)} 之一`);
    return;
  }
  if (spec.fields) {
    if (actual !== 'object') return; // 已由上面类型检查拦截
    validateObject(`${label}.${name}`, value, spec, errorsOut);
  }
  if (spec.items) {
    for (const [index, item] of value.entries()) {
      if (typeOf(item) !== 'object') {
        errorsOut.push(`${label}.${name}[${index}] 须为对象`);
        continue;
      }
      validateObject(`${label}.${name}[${index}]`, item, spec.items, errorsOut);
    }
  }
}

function validateObject(label, input, spec, errorsOut) {
  const allowed = Object.keys(spec.fields);
  for (const key of Object.keys(input)) {
    if (!allowed.includes(key)) errorsOut.push(`${label} 含未知字段 ${key}（允许：${allowed.join(', ')}）`);
  }
  const out = {};
  for (const [name, field] of Object.entries(spec.fields)) {
    const value = input[name];
    if (value === undefined) {
      if (field.req) errorsOut.push(`${label} 缺少必填字段 ${name}`);
      else if (field.def !== undefined) out[name] = typeof field.def === 'function' ? field.def() : field.def;
      continue;
    }
    checkField(label, name, field, value, errorsOut);
    out[name] = value;
  }
  return out;
}

function validateInput(command, input) {
  const spec = COMMAND_SPECS[command];
  if (!spec || !spec.fields) return input;
  const errorsOut = [];
  const validated = validateObject(command, input, spec, errorsOut);
  if (errorsOut.length) {
    throw new ServiceError(`${command} 入参校验失败：${errorsOut.join('；')}`);
  }
  return validated;
}

const PATH_ITEM_SPEC = {
  fields: {
    code: { type: 'string', req: true },
    desc: { type: 'string', req: true },
  },
};

const FUNCTION_PAYLOAD_SPEC = {
  fields: {
    actions: { type: 'array', nullable: true, items: PATH_ITEM_SPEC },
    interfaces: { type: 'array', nullable: true, items: PATH_ITEM_SPEC },
  },
};

const RESOURCE_REF_SPEC = {
  fields: {
    id: { union: ['string', 'number'] },
    resName: { type: 'string' },
    resUrl: { type: 'string' },
    resCode: { type: 'string' },
    resType: { type: 'string', enumValues: ['1', '4', '5'] },
    parentResId: { union: ['string', 'number'] },
  },
};

const COMMAND_SPECS = {
  'app-info': {
    fields: { uapName: { type: 'string', req: true } },
  },
  'find-resource': {
    fields: {
      appId: { type: 'string', req: true },
      id: { union: ['string', 'number'] },
      resName: { type: 'string' },
      resUrl: { type: 'string' },
      resCode: { type: 'string' },
      resType: { type: 'string', enumValues: ['1', '4', '5'] },
      parentResId: { union: ['string', 'number'] },
      parentResName: { type: 'string' },
    },
  },
  'create-menu': {
    fields: {
      appId: { type: 'string', req: true },
      resName: { type: 'string', req: true },
      resUrl: { type: 'string', req: true },
      resType: { type: 'string', enumValues: ['1'] },
      parentResId: { union: ['string', 'number'], nullable: true },
      status: { type: 'number', def: 1 },
      visible: { type: 'number', def: 1 },
      accountLine: { type: 'number', def: 1 },
      order: { type: 'number' },
      single: { type: 'number', req: true, enumValues: [0, 1] },
      domain: { type: 'string', def: '' },
      contractUrl: { type: 'string', def: '' },
      iframeUrl: { type: 'string', def: '' },
      resDesc: { type: 'string', def: '' },
      imagePath: { type: 'string', def: '' },
    },
  },
  'create-function': {
    fields: {
      appId: { type: 'string', req: true },
      parentResId: { union: ['string', 'number'], req: true },
      resName: { type: 'string', req: true },
      resCode: { type: 'string', req: true },
      resType: { type: 'string', enumValues: ['5'] },
      status: { type: 'number', def: 1 },
      accountLine: { type: 'number', def: 1 },
      buttonUrls: { type: 'string', req: true },
      interfaceUrls: { type: 'string', def: '' },
      function: { type: 'object', req: true, fields: FUNCTION_PAYLOAD_SPEC.fields },
    },
  },
  'update-menu': {
    fields: {
      id: { union: ['string', 'number'], req: true },
      appId: { type: 'string', req: true },
      resName: { type: 'string' },
      resUrl: { type: 'string' },
      resType: { type: 'string', enumValues: ['1'] },
      parentResId: { union: ['string', 'number'], nullable: true },
      status: { type: 'number' },
      visible: { type: 'number' },
      accountLine: { type: 'number' },
      order: { type: 'number' },
      single: { type: 'number', enumValues: [0, 1] },
      domain: { type: 'string' },
      contractUrl: { type: 'string' },
      iframeUrl: { type: 'string' },
      resDesc: { type: 'string' },
      imagePath: { type: 'string' },
    },
  },
  'update-function': {
    fields: {
      id: { union: ['string', 'number'], req: true },
      appId: { type: 'string', req: true },
      parentResId: { union: ['string', 'number'], req: true },
      resName: { type: 'string' },
      resCode: { type: 'string' },
      resType: { type: 'string', enumValues: ['5'] },
      status: { type: 'number' },
      accountLine: { type: 'number' },
      buttonUrls: { type: 'string' },
      interfaceUrls: { type: 'string' },
      function: { type: 'object', fields: FUNCTION_PAYLOAD_SPEC.fields },
    },
  },
  'update-button': {
    fields: {
      id: { union: ['string', 'number'], req: true },
      appId: { type: 'string', req: true },
      parentResId: { union: ['string', 'number'], req: true },
      resName: { type: 'string' },
      resCode: { type: 'string' },
      resType: { type: 'string', enumValues: ['4'] },
      status: { type: 'number' },
      accountLine: { type: 'number' },
    },
  },
  'get-user-roles': {
    fields: {
      appId: { type: 'string', req: true },
      uId: { type: 'string', def: '12436' },
      roleName: { type: 'string' },
    },
  },
  'assign-user-roles': {
    fields: {
      appId: { type: 'string', req: true },
      uId: { type: 'string', def: '12436' },
      addRoleNames: { type: 'array' },
      removeRoleNames: { type: 'array' },
      addRoleIds: { type: 'array' },
      removeRoleIds: { type: 'array' },
    },
  },
  'preview-role-permissions': {
    fields: {
      appId: { type: 'string', req: true },
      roleId: { type: 'string' },
      roleName: { type: 'string' },
      add: { type: 'array', items: RESOURCE_REF_SPEC },
      remove: { type: 'array', items: RESOURCE_REF_SPEC },
      uId: { type: 'string', def: '12436' },
    },
  },
  'update-role-permissions': {
    fields: {
      appId: { type: 'string', req: true },
      roleId: { type: 'string' },
      roleName: { type: 'string' },
      add: { type: 'array', items: RESOURCE_REF_SPEC },
      remove: { type: 'array', items: RESOURCE_REF_SPEC },
      uId: { type: 'string', def: '12436' },
    },
  },
};

const WRITE_COMMANDS = new Set(['create-menu', 'create-function', 'update-menu', 'update-function', 'update-button', 'assign-user-roles', 'update-role-permissions']);

// ---------------------------------------------------------------------------
// CLI
// ---------------------------------------------------------------------------

function camelFlag(name) {
  return name.replace(/-([a-z])/g, (_m, c) => c.toUpperCase());
}

function parseArgv(argv) {
  const positional = [];
  const flags = {};
  let yes = false;
  let jsonInput = null;
  for (let i = 0; i < argv.length; i++) {
    const token = argv[i];
    if (token === '--yes') {
      yes = true;
      continue;
    }
    if (token === '--json') {
      const raw = argv[++i];
      if (raw === undefined) throw new ServiceError('--json 缺少 JSON 值');
      try {
        jsonInput = JSON.parse(raw);
      } catch (exc) {
        throw new ServiceError(`--json 不是合法 JSON：${exc instanceof Error ? exc.message : String(exc)}`);
      }
      if (!jsonInput || typeof jsonInput !== 'object' || Array.isArray(jsonInput)) {
        throw new ServiceError('--json 须为 JSON 对象');
      }
      continue;
    }
    if (token.startsWith('--')) {
      const key = camelFlag(token.slice(2));
      const value = argv[++i];
      if (value === undefined) throw new ServiceError(`参数 ${token} 缺少值`);
      flags[key] = value;
      continue;
    }
    positional.push(token);
  }
  return { command: positional[0], positional, flags, yes, jsonInput };
}

function coerceFlags(command, flags) {
  const spec = COMMAND_SPECS[command];
  if (!spec) return flags;
  const out = { ...flags };
  for (const [name, field] of Object.entries(spec.fields)) {
    if (out[name] === undefined) continue;
    if (field.type === 'number' || (field.union && field.union.includes('number') && field.union.length === 1)) {
      const num = Number(out[name]);
      if (!Number.isFinite(num)) throw new ServiceError(`${command}.${name} 须为数字，实际 ${out[name]}`);
      out[name] = num;
    }
  }
  return out;
}

const USAGE = `用法：node uap.mjs <command> [--flag value ...] [--json '<JSON 对象>'] [--yes]

命令（读写语义与 @ane/uap-mcp 的 11 个 MCP 工具一一对应）：
  ping                         连通性自检（initialize + tools/list，验证网关配置）
  app-info --uap-name 天象      应用中文名 → appId（读本地快照，不打网关）
  find-resource                按 id/名/路由/resCode 查菜单、功能点、旧按钮（读）
  create-menu                  创建菜单（写，--yes）
  create-function              创建功能点 resType=5（写，--yes）
  update-menu / update-function / update-button   更新（写，--yes）
  get-user-roles               查用户已绑角色（读）
  assign-user-roles            用户角色增删（写，--yes）
  preview-role-permissions     预览角色权限变更（读）
  update-role-permissions      角色权限增删（写，--yes；先 preview 再执行）
  call <gateway-tool> --json   原始网关 tools/call 逃生口（白名单 9 工具）

扁平字段可直接用 kebab-case 旗标（如 --app-id max --res-name 名）；数组/嵌套对象
（function、add、remove、addRoleNames 等）必须走 --json。写命令必须带 --yes，
且执行前须先向用户展示拟变更并取得当前消息确认。详见 references/uap-tool-recipes.md。`;

async function main() {
  const argv = process.argv.slice(2);
  if (!argv.length || argv[0] === 'help' || argv[0] === '--help') {
    console.log(USAGE);
    return;
  }
  const { command, positional, flags, yes, jsonInput } = parseArgv(argv);

  if (!command || command === 'help' || command === '--help') {
    console.log(USAGE);
    return;
  }

  if (command === 'ping') {
    const config = loadGatewayConfig();
    const client = new GatewayClient(config);
    try {
      await client.open();
      const result = await client.request('tools/list', {});
      const tools = (result?.tools || []).map((tool) => tool.name).filter(Boolean);
      printOk({ ok: true, gateway: config.url, protocolVersion: client.protocolVersion, serverInfo: client.serverInfo, tools });
    } finally {
      await client.close();
    }
    return;
  }

  if (command === 'call') {
    const toolName = positional[1];
    if (!toolName) throw new ServiceError('call 命令须提供网关工具名（如 uap-api_tools_uap_resource_tree）');
    const config = loadGatewayConfig();
    const client = new GatewayClient(config);
    try {
      const result = await client.callTool(toolName, jsonInput || {});
      const data = parseToolText(result);
      const out = {
        http_status: result && result.isError ? 502 : 200,
        request: { gateway: config.url, method: 'tools/call', tool: toolName, arguments: jsonInput || {} },
        data,
      };
      if (result && result.isError) throw new ServiceError(`MCP Gateway 工具返回错误：tool=${toolName}`, { payload: out });
      printOk(out);
    } finally {
      await client.close();
    }
    return;
  }

  if (!COMMAND_SPECS[command]) {
    throw new ServiceError(`未知命令：${command ?? '(空)'}。\n${USAGE}`);
  }

  if (WRITE_COMMANDS.has(command) && !yes) {
    throw new ServiceError(
      `${command} 是写操作，必须带 --yes。执行前须先向用户展示拟变更（update-role-permissions 先跑 preview-role-permissions；create/update 先回读参数与目标父目录）并取得当前消息确认。`,
    );
  }

  const merged = { ...coerceFlags(command, flags), ...(jsonInput || {}) };
  const input = validateInput(command, merged);

  // app-info 读本地快照，不依赖网关
  if (command === 'app-info') {
    printOk(resolveApplication(itemsFromApplicationAll(loadApplicationAll().data), input.uapName));
    return;
  }

  const config = loadGatewayConfig();
  const client = new GatewayClient(config);
  try {
    switch (command) {
      case 'find-resource':
        printOk(await resourceLookup(client, input));
        break;
      case 'create-menu':
        printOk(await resourceAdd(client, input));
        break;
      case 'create-function':
        printOk(await resourceAddButton(client, input));
        break;
      case 'update-menu':
        printOk(await resourceEditMenu(client, input));
        break;
      case 'update-function':
        printOk(await resourceEditFunction(client, input));
        break;
      case 'update-button':
        printOk(await resourceEditButton(client, input));
        break;
      case 'get-user-roles':
        printOk(await roleGetUserRoleList(client, input));
        break;
      case 'assign-user-roles':
        printOk(await userSaveRole(client, input));
        break;
      case 'preview-role-permissions':
        printOk(await roleIntent(client, input, false));
        break;
      case 'update-role-permissions':
        printOk(await roleIntent(client, input, true));
        break;
      default:
        throw new ServiceError(`未知命令：${command}`);
    }
  } finally {
    await client.close();
  }
}

if (typeof fetch !== 'function') {
  console.error('需要 Node.js >= 18（全局 fetch）');
  process.exit(1);
}

main().catch((exc) => printErrorAndExit(exc));
