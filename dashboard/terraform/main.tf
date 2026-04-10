# Select cloud provider to use
provider "aws" {
    region     = var.AWS_REGION
    access_key = var.AWS_ID
    secret_key = var.AWS_SECRET
}

# Referring to existing resources

# Data
data "aws_vpc" "c21-vpc" {
    id = var.VPC_ID
}

data "aws_ami" "ec2_ami" {
    most_recent = true
    owners      = var.AMI_OWNERS

    filter {
        name   = "name"
        values = [var.AMI_NAME]
    }

    filter {
        name   = "architecture"
        values = [var.AMI_ARCH]
    }
}


# Security group (DB)
resource "aws_security_group" "jordan-museum-db-sg" {
    name   = "c21-jordan-museum-db-sg"
    vpc_id = data.aws_vpc.c21-vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "db-sg-inbound-postgres" {
    security_group_id = aws_security_group.jordan-museum-db-sg.id
    cidr_ipv4         = "0.0.0.0/0"
    from_port         = 5432
    ip_protocol       = "tcp"
    to_port           = 5432
}

resource "aws_db_instance" "c21-jordan-museum-db" {
    allocated_storage           = 10
    identifier                  = "c21-jordan-museum-db"
    db_name                     = "lmnh_museum"
    engine                      = "postgres"
    engine_version              = "17.6"
    instance_class              = "db.t3.micro"
    publicly_accessible         = true
    performance_insights_enabled = false
    skip_final_snapshot         = true
    db_subnet_group_name        = "c21-public-subnet-group"
    vpc_security_group_ids      = [aws_security_group.jordan-museum-db-sg.id]
    username                    = var.DB_USERNAME
    password                    = var.DB_PASSWORD
}

resource "aws_security_group" "c21-jordan-lmnh-ec2-sg" {
    name   = var.EC2_SG_NAME
    vpc_id = data.aws_vpc.c21-vpc.id
}

resource "aws_vpc_security_group_ingress_rule" "ec2-ssh" {
    security_group_id = aws_security_group.c21-jordan-lmnh-ec2-sg.id
    cidr_ipv4         = var.SSH_CIDR
    from_port         = 22
    to_port           = 22
    ip_protocol       = "tcp"
}

resource "aws_vpc_security_group_egress_rule" "ec2-egress-all" {
    security_group_id = aws_security_group.c21-jordan-lmnh-ec2-sg.id
    cidr_ipv4         = "0.0.0.0/0"
    ip_protocol       = "-1"
}


resource "aws_instance" "c21-jordan-lmnh-ec2" {
    ami                    = data.aws_ami.ec2_ami.id
    instance_type          = var.EC2_INSTANCE_TYPE
    subnet_id              = var.SUBNET_ID
    vpc_security_group_ids = [aws_security_group.c21-jordan-lmnh-ec2-sg.id]
    key_name               = var.KEY_NAME
    associate_public_ip_address = true
    

    tags = {
        Name = var.EC2_NAME
    }
}