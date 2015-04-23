manage="${VENV}/bin/python ${INSTALLDIR}/${REPO}/django_refugeerights/manage.py"

if [ ! -f ${INSTALLDIR}/clinicfinder-installed ]; then
    su - postgres -c "createdb django_refugeerights"
    su - postgres -c "psql django_refugeerights -c 'CREATE EXTENSION hstore; CREATE EXTENSION postgis; CREATE EXTENSION postgis_topology;'"

    mkdir ${INSTALLDIR}/${REPO}/django_refugeerights/static

    chown -R ubuntu:ubuntu ${INSTALLDIR}/${REPO}/media
    chown -R ubuntu:ubuntu ${INSTALLDIR}/${REPO}/static

    $manage syncdb --noinput
    $manage collectstatic --noinput
    touch ${INSTALLDIR}/refugeerights-installed
else
    $manage migrate --noinput
    $manage collectstatic --noinput
fi