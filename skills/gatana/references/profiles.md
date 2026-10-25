# Profiles in Gatana

Use this file to create, change, assign or explain a profile.

Docs: [Profiles](https://docs.gatana.ai/profiles/), [Connected clients](https://docs.gatana.ai/connected-clients/), [Code Mode](https://docs.gatana.ai/code-mode/), [Permissions and roles](https://docs.gatana.ai/permissions-and-roles/).

## Contents

- [What a profile is](#what-a-profile-is)
- [Settings](#settings)
- [How a profile becomes active](#how-a-profile-becomes-active)
- [Create and fill a profile](#create-and-fill-a-profile)
- [Tool configuration](#tool-configuration)
- [Profile credentials](#profile-credentials)
- [Maintainers](#maintainers)
- [Recipes](#recipes)
- [Dashboard steps](#dashboard-steps)

## What a profile is

A profile is a named set of:

- **Servers.** Each server in the profile gives member access to everyone who has the profile active.
- **Tool settings** for each of these servers: which tools are available, their exposed names, and which tools stay visible in Code Mode.
- **Credentials** for each of these servers. They override the server and user credentials.
- **Session flags**: restrictive mode and forced Code Mode.

Use a profile when access or credentials must depend on **who calls** or **which client calls**. Use server membership when a person or team needs the server everywhere.

Several profiles can be active at the same time. Their servers add up. Their tool selections add up (union). For credentials and for name conflicts, the profile with the highest priority wins. See [credentials.md](credentials.md#how-gatana-finds-the-credential-for-a-call).

## Settings

| Field                 | Meaning                                                                                                                                                                                                                                            |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`, `description` | Shown in the dashboard.                                                                                                                                                                                                                            |
| `isOpenToAllUsers`    | Every member can apply the profile themselves: with `?p=`, the header, a token or a client. **Risk:** every member then gets member access to all servers in the profile. Closing an open profile also removes it from all personal access tokens. |
| `isRestrictive`       | A session with this profile reaches only the servers of this profile. This applies to organization owners too. Use it for agents and isolated work.                                                                                                |
| `isCodeModeForced`    | Sessions with this profile run in Code Mode for all servers, not only the profile's servers. Gatana adds the built-in `codemode` server to the profile. If that server is not installed yet, only an organization owner can turn on the flag.      |

## How a profile becomes active

| Method                                                    | Who can do it                                             | Notes                                                                                |
| --------------------------------------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Direct assignment to a user or service account            | The user for themselves. Organization owners for anybody. | Owners can **lock** it: the user cannot remove it, and it wins credential conflicts. |
| Direct assignment to a team                               | Team maintainers. Organization owners.                    | Owners can lock it.                                                                  |
| Claim mapping                                             | Profile maintainers                                       | Applies at sign-in when an identity-provider claim matches.                          |
| Personal access token                                     | The token owner. Owners for service-account tokens.       | Dashboard only (needs a browser session).                                            |
| Connected OAuth client                                    | The user who connected the client                         | `patchConnectedClient({ clientId, body: { profileIds } })`.                          |
| `?p=<id>` on the MCP URL, or header `x-gatana-profile-id` | Anybody                                                   | Only open profiles. Comma-separated list. A closed profile gives HTTP 400.           |

Tokens and clients can carry profiles that are open, or that the user can manage.

Claim mappings match like this, for the claims `{ "department": "eng", "groups": ["eng", "platform"], "branch": { "office": "london" } }`:

| `claimKey`      | `claimValue` | Matches because                 |
| --------------- | ------------ | ------------------------------- |
| `department`    | `eng`        | Direct value.                   |
| `groups`        | `platform`   | The array has the value.        |
| `branch.office` | `london`     | Dot notation for nested values. |

## Create and fill a profile

```typescript
// 1. Create. A new profile has no servers.
const { profile } = await codemode.gatanaApi.createProfile({
  body: {
    name: 'CI agent',
    description: 'GitHub and Sentry for the CI review agent',
    isOpenToAllUsers: false,
    isRestrictive: true,
  },
});

// 2. Set the servers. serverIds replaces the full list.
await codemode.gatanaApi.updateProfile({
  profileId: profile.id,
  body: { serverIds: ['github', 'sentry'] },
});

// 3. Assign it.
await codemode.gatanaApi.createUserProfile({ userId, body: { profileId: profile.id } });
await codemode.gatanaApi.createTeamProfile({ teamId, body: { profileId: profile.id, isLockedByOrgOwner: false } });
await codemode.gatanaApi.createProfileClaimMapping({
  profileId: profile.id,
  body: { claimKey: 'groups', claimValue: 'ci' },
});
```

**`serverIds` replaces the full list.** Send slugs: every Gatana version accepts them. Newer versions also accept server IDs and refuse a value that matches no server. Older versions accept only slugs, and they remove the servers that they cannot match. To add one server:

```typescript
const { profile } = await codemode.gatanaApi.getProfile({ profileId });
const slugs = profile.servers.map(s => s.slug);
await codemode.gatanaApi.updateProfile({ profileId, body: { serverIds: [...slugs, 'new-server'] } });
```

You can add a server to a profile only if you can read that server. Removing a server from a profile discards its tool configuration for that profile.

With the CLI, the same steps are:

```bash
gatana create profile "CI agent" --description "GitHub and Sentry for the CI review agent" --restrictive -s github -s sentry
gatana profile assign "CI agent" --account ci@service-account.acme.gatana
gatana profile assign "CI agent" --team platform
gatana profile claims add "CI agent" groups=ci
gatana profile add-server "CI agent" new-server
```

Other operations: `listProfiles({ serverSlug? })`, `listProfileDirectAssignments`, `listProfileClaimMappings`, `deleteProfileClaimMapping`, `deleteUserProfile`, `deleteTeamProfile`, `patchUserProfile` (lock or unlock, owners only), `deleteProfile`. To see what a user or team can reach, use `getMcpServersAccessPreview({ userId })` or `({ teamId })`.

## Tool configuration

For each server in a profile, `updateProfileServerTools` sets the tools. It **replaces** the configuration for that server, so read it first with `listProfileTools({ profileId })` and keep the entries you need.

```typescript
await codemode.gatanaApi.updateProfileServerTools({
  profileId,
  serverSlug: 'github',
  body: {
    areAllToolsEnabled: false, // true: every enabled tool of the server
    autoEnableNewTools: false, // when false: new tools stay off until somebody adds them
    tools: [
      { toolName: 'get_pull_request', isPromoted: false, toolNameOverride: '' },
      { toolName: 'create_review', isPromoted: true, toolNameOverride: 'review-pr' },
    ],
  },
});
```

- `areAllToolsEnabled: true`: all enabled tools are available. `tools` then holds only the tools that you rename or promote.
- `areAllToolsEnabled: false`: only the tools in `tools` are available.
- `toolName` is the name that the server reports, without the slug prefix.
- `toolNameOverride`: the name that clients see instead of `<slug>_<tool>`. Letters, digits and hyphens, 64 characters or fewer, no underscores, unique in the profile. Empty keeps the normal name. The normal name still works for calls.
- `isPromoted: true`: the tool stays in the tool list when the session runs in Code Mode.
- A tool that is disabled on the server stays unavailable. The profile cannot turn it on.
- Tool selection applies to calls over MCP and over the REST API.
- The selection limits the server for the whole session, also when the user reaches the server through membership. A tool is available when no active profile includes its server, or when at least one active profile allows it.

## Profile credentials

Set a credential for one server and one profile:

```typescript
// Best: the user types the secret into Gatana.
const { url } = await codemode.gatanaApi.getMcpServerCredentialsAuthorizeUrl({
  serverSlug: 'github',
  scope: 'profile',
  profileId,
  returnTo: 'thank-you-page',
});
// Or, if the user gave you the value:
await codemode.gatanaApi.updateMcpServerCredentialsProfile({
  serverSlug: 'github',
  profileId,
  body: { type: 'apikey', apikeys: [['GITHUB_TOKEN', '<value>']] },
});
// Or copy an existing credential, for example one user's login, to the profile:
await codemode.gatanaApi.copyMcpServerCredentials({ serverSlug: 'github', id: credentialId, to: 'profile', profileId });
```

A profile credential is used only when it has the same type as the server's method, and for API keys the same number of keys. For OAuth, everybody with the profile acts as the account that signed in.

## Maintainers

Each profile has maintainers. They can change the profile, its servers, tools, credentials, claim mappings and assignments, add and remove maintainers, and delete the profile. The creator is the first maintainer. Organization owners can always manage all profiles. A profile always keeps at least one maintainer.

A maintainer can manage the profile's credentials on all of its servers, also on servers where the maintainer is not a member.

Operations: `listProfileMaintainers`, `createProfileMaintainer({ profileId, body: { userId } })`, `deleteProfileMaintainer({ profileId, userId })`.

## Recipes

| Goal                                                | Setup                                                                                                                                                                           |
| --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| One shared login for a team on a user-scoped server | Profile with the server and a profile credential. Assign the profile to the team.                                                                                               |
| A different credential for each MCP client          | One profile per client, each with its own credential. Attach each profile to the client's token or connected client.                                                            |
| An agent that may use only two servers              | Restrictive profile with the two servers. Attach it to the agent's token, or use `?p=` if the profile is open.                                                                  |
| Read-only GitHub for contractors                    | Profile with GitHub, `areAllToolsEnabled: false`, only the read tools. Assign it to the contractors team. The profile gives the access, so the team needs no server membership. |
| Many tools, small context                           | Profile with `isCodeModeForced: true`. Promote the few tools that must stay visible.                                                                                            |
| Access from the identity provider                   | Claim mapping on the profile, for example `groups` = `finance`.                                                                                                                 |

## Dashboard steps

1. Open **Profiles** in the left sidebar. Click **Create profile**, or open a profile.
2. Set the name, the description and the flags.
3. Add servers. Click **Edit** on a server row to set its tools and credentials.
4. Add claim mappings and maintainers on the same page.
5. To assign: **People & Accounts** > the account > **Profiles** > **Assign profile**, or **Teams** > the team > **Profiles** > **Assign profile**.
6. For a token or a client: **Clients & API Keys** > **Edit** on the token or client.
