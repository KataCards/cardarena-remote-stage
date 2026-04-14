module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    // Enforce standard Conventional Commit types
    "type-enum": [
      2,
      "always",
      [
        "feat",     // new feature → bumps MINOR
        "fix",      // bug fix     → bumps PATCH
        "perf",     // performance improvement → bumps PATCH
        "revert",   // revert a commit
        "docs",     // documentation only
        "style",    // formatting, missing semicolons, etc.
        "refactor", // code change that is neither feat nor fix
        "test",     // adding or updating tests
        "build",    // build system / external dependencies
        "ci",       // CI configuration files and scripts
        "chore",    // other changes that don't modify src or test
      ],
    ],
    "subject-case": [2, "never", ["start-case", "pascal-case", "upper-case"]],
  },
};
