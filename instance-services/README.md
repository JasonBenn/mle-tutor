To copy the service file to the server:

```bash
sudo cp /opt/mle-tutor/instance-services/mle-tutor.service /etc/systemd/system/
```

To enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable mle-tutor.service
sudo systemctl start mle-tutor.service
```
