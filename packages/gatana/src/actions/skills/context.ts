import { ConfigLoader, FileConfigStrategy, Gatana } from 'gatana-sdk';
import { extractTenantFromUrl, getDefaultOrganization } from 'gatana-sdk/config';
import { createSkillsApi, type SkillsApi } from './api.js';
import type { SkillsIdentity } from './sync.js';

export interface SkillsContext extends SkillsIdentity {
  api: SkillsApi;
}

/**
 * The organization a skills command works against. `--org` picks one from the config file; without
 * it the CLI's resolved configuration is used. The organization id is recorded in every manifest
 * and SKILL.md, so it must be known even when only a base URL is: the first host label is the
 * tenant.
 *
 * The generated client is a module-level singleton, so constructing a second Gatana re-points
 * every v1 call in this process. The skills commands make no other calls, so that is fine here.
 */
export function resolveSkillsContext(gatana: Gatana, orgOption?: string): SkillsContext {
  let client = gatana;
  if (orgOption) {
    let config;
    try {
      config = new ConfigLoader([new FileConfigStrategy(orgOption)]).getConfig();
    } catch {
      throw new Error(`Organization ${orgOption} is not configured. Run "gatana config login ${orgOption}" first`);
    }
    client = new Gatana({ config, isCli: true });
  }
  const baseUrl = client.config.baseUrl;
  const orgId =
    orgOption ??
    process.env.GATANA_ORG_ID ??
    (process.env.GATANA_API_KEY ? undefined : getDefaultOrganization()) ??
    extractTenantFromUrl(baseUrl);
  return { orgId, baseUrl, api: createSkillsApi(client) };
}
