# Commit the Jsonnet vendor/ directory

The `grafonnet/vendor/` directory (managed by jsonnet-bundler) is committed to the repository rather than gitignored. This makes the repo self-contained — `grr apply` works immediately after clone without running `jb install` first. The Jsonnet community convention is to commit `vendor/`, analogous to committing `go.sum` in Go projects. The trade-off is a larger initial clone; the benefit is reproducibility without a build step.
