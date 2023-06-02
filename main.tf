terraform {
  required_providers {
    google = "~> 3.70.0"
    microsoftteams = "~> 0.1.0"
  }

  provider google {
    project = var.gcp_project_id
    region = var.gcp_region
  }

  provider microsoftteams {
    endpoint = var.microsoft_teams_endpoint
    app_id = var.microsoft_teams_app_id
    app_secret = var.microsoft_teams_app_secret
  }

  resource "google_pubsub_topic" "sccfindings" {
    name = "scc-findings"
  }

  resource "google_cloudfunctions_function" "cf" {
    name = "scc-teams-notifier"
    description = "Security Command Center findings notifier to Microsoft Teams"
    runtime = "python39"
    timeout = 540
    available_memory_mb = 256
    max_instances = 1
    ingress_settings = "ALLOW_INTERNAL_AND_GCLB"

    environment_variables = {
      MICROSOFT_TEAMS_WEBHOOK_URL = var.microsoft_teams_webhook_url
    }

    source_archive_bucket = google_storage_bucket.function_bucket.name
    source_archive_object = google_storage_bucket_object.zip.name

    event_trigger {
      event_type = "providers/google.pubsub/eventTypes/topic.publish"
      resource = google_pubsub_topic.sccfindings.id
      failure_policy {
        retry = true
      }
    }
  }

  resource "google_storage_bucket" "function_bucket" {
    name = "scc-teams-notifier-cf-bucket"
  }

  resource "google_storage_bucket_object" "zip" {
    name = "cf-scc-notification.zip"
    bucket = google_storage_bucket.function_bucket.name
    source = "./app/scc-finding-teams-notifications/cf-scc-notification.zip"
  }

  output "function_url" {
    value = google_cloudfunctions_function.cf.https_trigger_url
  }
}
