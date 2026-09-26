output "crypto_key_id" {
  description = "Pass this value as kms_crypto_key_id to the notifier module."
  value       = google_kms_crypto_key.this.id
}

output "encrypt_command" {
  description = "Command that encrypts the Microsoft Teams webhook URL for teams_webhook_url_ciphertext."
  value       = <<-EOT
    printf '%s' "$TEAMS_WEBHOOK_URL" | gcloud kms encrypt \
      --project ${var.project_id} \
      --location ${var.kms_location} \
      --keyring ${google_kms_key_ring.this.name} \
      --key ${google_kms_crypto_key.this.name} \
      --plaintext-file - \
      --ciphertext-file - | base64 | tr -d '\n'
  EOT
}
