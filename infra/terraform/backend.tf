terraform {
  backend "s3" {
    bucket = "discovery-terraform-state"
    key    = "global/platform.tfstate"
    region = "us-east-1"
    encrypt = true
    dynamodb_table = "discovery-terraform-locks"
  }
}
