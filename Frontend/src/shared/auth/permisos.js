export function tienePermiso(profile, permiso) {
  return profile?.usuario.es_propietario === true || profile?.permisos?.includes(permiso) === true
}
