
output "db_endpoint" {
    description = "RDS endpoint"
    value       = aws_db_instance.c21-jordan-museum-db.address
}

output "db_port" {
    description = "RDS port"
    value       = aws_db_instance.c21-jordan-museum-db.port
}

output "c21-jordan-ec2_instance_id" {
    value = aws_instance.c21-jordan-lmnh-ec2
}

output "c21-jordan-ec2_public_ip" {
    value = aws_instance.c21-jordan-lmnh-ec2
}

output "c21-jordan-ec2_sg_id" {
    value = aws_security_group.c21-jordan-lmnh-ec2-sg
}

output "c21-jordan-ec2_ami_id" {
    value = data.aws_ami.ec2_ami.id
}