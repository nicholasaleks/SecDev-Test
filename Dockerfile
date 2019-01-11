FROM python

RUN touch super_secret.secret
RUN chmod 000 super_secret.secret
RUN touch super_secret.secret.old
RUN touch root/passwords.secret
RUN touch /lib/lsb secret_config.config
RUN touch var/lib/systemd/deb-systemd-helper-enabled/definitely-not-passwords.secret
RUN mkdir /var/lib/secrets
RUN touch /var/lib/secrets/clients.secret
RUN chmod 000 /var/lib/secrets/clients.secret
RUN chmod 000 /var/lib/secrets

ADD AutomatedCollection.py /

RUN python AutomatedCollection.py --src / --dest /collect --target_extensions .secret .old --target_regex secret* --archive true --archive_name collect.tar.gz --upload False --clean_dest False
ENTRYPOINT ["tail", "-f", "/dev/null"]
