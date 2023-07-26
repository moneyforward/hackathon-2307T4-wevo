Docker kill wevo-be
Docker rm wevo-be
Docker build -t wevo-be .
Docker run -p 8080:8080 --name wevo-be wevo-be:latest
