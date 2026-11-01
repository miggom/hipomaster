# Secretos (sops + age)

- `vm.enc.env` y `scraper.enc.env`: cifrados con la clave pública age de doc y de core-01.
- Crear: `sops --encrypt --age <pubkeys> ../vm/.env > vm.enc.env`
- Editar: `sops vm.enc.env`
- Nunca subir ficheros sin cifrar. La clave privada age se guarda en el gestor de contraseñas.
