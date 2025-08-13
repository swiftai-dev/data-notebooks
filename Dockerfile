# 1. Use base image "daskdev/dask:latest-py3.11"
FROM daskdev/dask:latest-py3.11

# 2. Install these packages "dask-cloudprovider httplib2 cryptography google-api-python-client"
RUN pip install "dask-cloudprovider" "httplib2" "cryptography" "google-api-python-client" "ipykernel"

# 3. then install gcloud cli
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-transport-https \
    ca-certificates \
    gnupg \
    curl \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && apt-get update && apt-get install -y google-cloud-sdk
