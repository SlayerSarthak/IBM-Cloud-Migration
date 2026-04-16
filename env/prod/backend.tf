terraform {
  backend "s3" {
    bucket                      = "ibm-prod-state"
    key                         = "terraform.tfstate"
    region                      = "us-standard"

    endpoints = {
      s3 = "https://s3.us-south.cloud-object-storage.appdomain.cloud"
    }

    access_key                  = "<your_cos_access_key>"
    secret_key                  = "<your_cos_secret_key>"

    skip_credentials_validation = true
    skip_region_validation      = true
    skip_requesting_account_id  = true
    force_path_style            = true
  }
}
