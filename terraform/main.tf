provider "aws" {
  region = "ap-south-1"
}

resource "aws_instance" "test" {
  ami = "ami-00f3bd567c56a466d"
  instance_type = "t2.micro"
  subnet_id = "subnet-0e0bbdsadsad5255"
  associate_public_ip_address = true
  vpc_security_group_ids = ["sg-076sdfsdf2311818"]

  tags = {
    Name = "app-ec2"
  }
}