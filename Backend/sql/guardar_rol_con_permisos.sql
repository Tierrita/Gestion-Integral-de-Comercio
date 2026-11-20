-- Aplicar con una credencial administrativa. Esta función solo debe ser invocada por el backend.
-- La transacción de cada llamada RPC es atómica: cualquier error revierte todos los cambios.
create or replace function public.guardar_rol_con_permisos(
    p_id_comercio integer,
    p_id_rol integer,
    p_nombre_rol text,
    p_permisos integer[]
)
returns integer
language plpgsql
security invoker
set search_path = ''
as $$
declare
    v_id_rol integer;
    v_id_permiso integer;
    v_permisos integer[];
begin
    if p_id_comercio is null then
        raise exception 'El comercio es obligatorio';
    end if;

    if p_permisos is not null and array_position(p_permisos, null) is not null then
        raise exception 'Los permisos no pueden contener valores nulos';
    end if;

    if p_permisos is not null then
        select coalesce(array_agg(distinct x), '{}'::integer[])
        into v_permisos
        from unnest(p_permisos) as x;

        if exists (
            select 1 from unnest(v_permisos) as x
            where not exists (select 1 from public.permisos p where p.id_permiso = x)
        ) then
            raise exception 'Se indicó un permiso inexistente';
        end if;
    end if;

    if p_id_rol is null then
        if p_nombre_rol is null or length(btrim(p_nombre_rol)) < 3 then
            raise exception 'El nombre del rol debe tener al menos 3 caracteres';
        end if;
        insert into public.roles (id_comercio, nombre_rol, estado)
        values (p_id_comercio, btrim(p_nombre_rol), true)
        returning id_rol into v_id_rol;
    else
        select r.id_rol into v_id_rol
        from public.roles r
        where r.id_rol = p_id_rol and r.id_comercio = p_id_comercio
        for update;
        if v_id_rol is null then
            raise exception 'Rol no encontrado en el comercio';
        end if;
        if p_nombre_rol is not null then
            if length(btrim(p_nombre_rol)) < 3 then
                raise exception 'El nombre del rol debe tener al menos 3 caracteres';
            end if;
            update public.roles set nombre_rol = btrim(p_nombre_rol)
            where id_rol = v_id_rol and id_comercio = p_id_comercio;
        end if;
    end if;

    if p_permisos is not null then
        delete from public.rol_permiso where id_rol = v_id_rol;
        insert into public.rol_permiso (id_rol, id_permiso)
        select v_id_rol, x from unnest(v_permisos) as x;
    end if;

    return v_id_rol;
end;
$$;

revoke all on function public.guardar_rol_con_permisos(integer,integer,text,integer[]) from public, anon, authenticated;
grant execute on function public.guardar_rol_con_permisos(integer,integer,text,integer[]) to service_role;
