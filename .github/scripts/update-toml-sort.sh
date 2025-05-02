#!/usr/bin/env bash
set -euo pipefail

file=".pre-commit-hooks.yaml"
latest_toml_sort=$(curl -s https://pypi.org/pypi/toml-sort/json | jq -r .info.version)

echo "Latest toml-sort: $latest_toml_sort"

if grep -q "toml-sort==${latest_toml_sort}" "$file"; then
  echo "toml-sort is already up to date"
  echo "updated=no" >> "$GITHUB_OUTPUT"
  exit 0
fi

# Update toml-sort version in the file
sed -i.bak -E "s/toml-sort==[0-9]+\.[0-9]+\.[0-9]+/toml-sort==${latest_toml_sort}/" "$file"
rm "$file.bak"

echo "Updated toml-sort version in ${file}"

# Bump patch version based on last Git tag
latest_tag=$(git tag --sort=-v:refname | grep '^v' | tail -n1)
if [[ -z "$latest_tag" ]]; then
  new_version="v0.1.0"
else
  IFS='.' read -r major minor patch <<< "${latest_tag#v}"
  new_patch=$((patch + 1))
  new_version="v${major}.${minor}.${new_patch}"
fi

echo "new_version=$new_version" >> "$GITHUB_OUTPUT"
echo "toml_sort_version=$latest_toml_sort" >> "$GITHUB_OUTPUT"
echo "updated=true" >> "$GITHUB_OUTPUT"
