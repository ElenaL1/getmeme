set -e

# Set MinIO client alias
docker exec -it get_mem-minio-1 mc alias set minio http://127.0.0.1:9000 getmem minio123

# Create bucket getmeme(ignore error if bucket already exists)
docker exec -it get_mem-minio-1 mc mb minio/getmeme || true

# Set public access to the bucket
docker exec -it get_mem-minio-1 mc anonymous set public minio/getmeme