#!/usr/bin/env bash
# Test of the Docker procedure in concept.md 4.13 on the development machine.
# Deletes only the test objects released by the user: container objective_payne,
# the two vsc-testprojekt images, build cache older than 48 h, and at the end
# the image of this throwaway compose project.
# Run: sudo bash /tmp/compose-probe/docker_test.sh 2>&1 | tee /tmp/docker_test.log

cd /tmp/compose-probe || exit 1
run() { echo; echo "\$ $*"; "$@"; }
step() { echo; echo "==== $*"; }
images() { docker images --format '{{.Repository}}:{{.Tag}}  {{.ID}}'; }

VSC=vsc-testprojekt-d70f365e072cb7dc044aee18672e986f3dbb27f0bd6b5d0a3ecd3e80197e6484

step "0 Ausgangslage"
run docker system df -v
run docker ps -a --format '{{.Names}}  {{.Image}}  {{.Status}}'
echo; echo "\$ images"; images
run docker volume ls
run docker inspect objective_payne --format '{{json .Mounts}}'

step "1 Compose: Projektname und Images laut Compose"
run docker compose config
run docker compose config --images

step "2 Compose: bauen und Container anlegen (nicht starten)"
run docker compose build
run docker compose create
echo; echo "\$ images"; images
run docker compose ls -a
run docker ps -a --filter label=com.docker.compose.project \
    --format '{{.Names}}  {{.Status}}  {{.Label "com.docker.compose.project"}}  {{.Label "com.docker.compose.project.config_files"}}'

step "3 Compose: herunterfahren (Images muessen bleiben)"
run docker compose down
run docker compose ls -a
echo; echo "\$ images"; images

step "4 Build-Cache: loeschen, was nicht juenger als 48 h ist"
run docker builder prune --all --force --filter until=48h
run docker system df -v

step "5 Beendeten Container loeschen, samt anonymen Volumes"
run docker rm -v objective_payne
run docker volume ls

step "6 Zweite Image-Pruefung"
used=$(docker ps -a --format '{{.Image}}' | sort -u)
keep=$(docker compose config --images | sed '/:/!s/$/:latest/')
echo; echo "In Gebrauch: ${used:-keine}"; echo "Erhalten-Liste: $keep"
echo; echo "Images ohne Container:"
images | while read -r name id; do
    grep -qxF "$name" <<<"$used" && continue
    if grep -qxF "$name" <<<"$keep"; then echo "  $name  -> erhalten (Compose)"
    else echo "  $name  -> Loeschkandidat"; fi
done
run docker rmi "$VSC-uid:latest" "$VSC:latest"
echo; echo "\$ images"; images

step "7 Testprojekt wieder entfernen"
run docker compose down --rmi local
echo; echo "\$ images"; images
