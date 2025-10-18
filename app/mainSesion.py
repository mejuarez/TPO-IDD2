from sesion import login_medico, verificar_sesion

# Hacer login
res = login_medico("dr_garcia", "contraseñaSegura123")
print(res)

# Guardar token
token = res.get("session_token")

# Verificar sesión
ver = verificar_sesion(token)
print(ver)