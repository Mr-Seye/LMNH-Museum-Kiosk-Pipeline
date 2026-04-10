variable "DB_USERNAME" {
    type = string
}

variable "DB_PASSWORD" {
    type = string
}

variable "AWS_REGION" {
    type    = string
    default = "eu-west-2"
}

variable "AWS_ID" {
    type = string
}

variable "AWS_SECRET" {
    type = string
}

variable "VPC_ID" {
    type = string
}

variable "SUBNET_ID" {
    type = string
    default = "subnet-0fbc8bed69fb32837"
}

variable "KEY_NAME" {
    type = string
}

variable "SSH_CIDR" {
    type        = string
    description = "Public IP in CIDR format"
}

variable "EC2_NAME" {
    type    = string
    default = "c21-jordan-lmnh-ec2"
}

variable "EC2_SG_NAME" {
    type    = string
    default = "c21-jordan-lmnh-ec2-sg"
}

variable "EC2_INSTANCE_TYPE" {
    type    = string
    default = "t2.nano"
}

variable "AMI_NAME" {
    type        = string
    description = "AMI name pattern to select (wildcards supported)."
}

variable "AMI_OWNERS" {
    type    = list(string)
    default = ["amazon"]
}

variable "AMI_ARCH" {
    type    = string
    default = "x86_64"
}
