# Google Cloud deployment

The below Google Cloud commands will need a few environment variables.

```shell
export PROJECT_ID={your google project id}
export SERVICE_ACCOUNT_NAME=github-service-account
export SERVICE_ACCOUNT=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
export WORKLOAD_IDENTITY_POOL=github-pool
export WORKLOAD_PROVIDER=github-provider
export REPO={your github user/repo}
```

Create a service account for the GitHub action.

```shell
gcloud auth login
gcloud config set project ${PROJECT_ID}
gcloud auth application-default login
gcloud services enable \
 iamcredentials.googleapis.com \
 run.googleapis.com \
 cloudbuild.googleapis.com \
 artifactregistry.googleapis.com \
 --project "${PROJECT_ID}"
gcloud iam service-accounts create "${SERVICE_ACCOUNT_NAME}" --project "${PROJECT_ID}"
```

Create a workload identity pool.

```shell
gcloud iam workload-identity-pools create "${WORKLOAD_IDENTITY_POOL}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="${WORKLOAD_IDENTITY_POOL}"
gcloud iam workload-identity-pools describe "${WORKLOAD_IDENTITY_POOL}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --format="value(name)"
```

Below environment variables are for the workload provider

```shell
export WORKLOAD_IDENTITY_POOL_ID={from above describe command}
```

Create a workload identity pool provider and describe the newly created provider.

```shell
gcloud iam workload-identity-pools providers create-oidc "${WORKLOAD_PROVIDER}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="${WORKLOAD_IDENTITY_POOL}" \
  --display-name="${WORKLOAD_PROVIDER}" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"
gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL_ID}/attribute.repository/${REPO}"
gcloud iam workload-identity-pools providers describe "${WORKLOAD_PROVIDER}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="${WORKLOAD_IDENTITY_POOL}" \
  --format="value(name)"
```

Give api permissions to the service account.

```shell
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/artifactregistry.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/run.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/viewer"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/iam.serviceAccountUser"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/cloudbuild.builds.viewer"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/cloudbuild.builds.builder"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/cloudsql.client"
gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" \
    --format='table(bindings.role)' \
    --filter="bindings.members:${SERVICE_ACCOUNT}"
```
