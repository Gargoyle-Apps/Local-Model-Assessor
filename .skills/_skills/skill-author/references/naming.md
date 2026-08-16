# Skill naming and prefixes

Read this reference only when deriving, choosing, or validating a new skill name.

## Default rule

Skills shipped by the upstream repository whose root directory is `skills-harness` are unprefixed. Skills authored in a consumer repository use `<repo-prefix>-<name>` so their ownership is visible and names do not collide across repositories.

Derive the default prefix from the consumer repository's root directory:

1. Split the directory name on hyphens, underscores, and whitespace; collapse consecutive separators.
2. Take the lowercase first letter of every non-empty segment.
3. Append `-`.

| Repository directory | Prefix |
|---|---|
| `ux-package-management` | `uxpm-` |
| `eng-package-management` | `epm-` |
| `git-minder` | `gm-` |
| `warehouse` | `w-` |
| `ware_house` | `wh-` |
| `Media Library` | `ml-` |
| `skills-harness` | none; upstream kit |

Use the prefixed form for the directory, frontmatter `name`, and generated index entry. Renaming an existing unprefixed consumer skill is out of scope unless the user asks.

## Declared prefixes

A consumer with multiple skill families, or an unsuitable derived prefix, may declare allowed prefixes in `.skills/_meta.yml`:

```yaml
kit_version: "1.0.0"
repo_url: "https://github.com/example/build-tools"
prefixes:
  - bld-
  - bin-
```

When `prefixes:` exists:

- Every consumer-authored skill starts with one listed prefix.
- Choose the prefix matching the skill family; ask the user only when context cannot decide safely.
- The list replaces the derived default. A single entry is the supported override for a single-family repo.
- Each entry ends in `-` and contains only lowercase alphanumerics and hyphens.
- Kit-bundled skills remain unprefixed.

When `prefixes:` is absent, use the derived default. Declare multiple prefixes only when one prefix cannot describe the repository's actual skill families. `.skills/_harness/migrate-to-subtree.sh` accepts the same declared list.
