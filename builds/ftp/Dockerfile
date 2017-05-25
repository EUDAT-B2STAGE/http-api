FROM stilliard/pure-ftpd

# startup
CMD /run.sh -c 50 -C 10 -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -R -P $PUBLICHOST -p 30000:30019

EXPOSE 21 30000-30019
