Docker build --platform=linux/amd64 -t wevo-be-amd .
Docker tag wevo-be-amd asia-northeast1-docker.pkg.dev/gen-ai-4-mfw/wevo/wevo-be
Docker push asia-northeast1-docker.pkg.dev/gen-ai-4-mfw/wevo/wevo-be
