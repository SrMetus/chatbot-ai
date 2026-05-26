# Changelog

## Sprint 2 — RAG + corpus notarial + carga de PDFs

### Nuevos endpoints
- `GET /api/v1/clients/{client_id}/widget-config` — endpoint público que expone la configuración de marca del widget (primary_color, bot_name, subtitle, welcome_message) sin filtrar datos sensibles del cliente.
- `PublicClientResponse` — schema que oculta email, phone y system_prompt en endpoints públicos de clientes.

### Modelo de datos
- Campo `subtitle` agregado al modelo `Client`.
- `DateTime(timezone=True)` aplicado a todos los modelos de SQLAlchemy para consistencia horaria.

### Admin panel
- Pestaña **Editar** con campo subtitle, código de instalación del widget y renderizado de Markdown.

### Widget embebido
- El widget ahora obtiene su configuración (colores, nombre, subtítulo, mensaje de bienvenida) desde `GET /widget-config` en lugar de usar solo valores fijos.
- Código de instalación simplificado: ya no incluye color ni bot-name en el embed.
- Fix XSS en `renderMarkdown` con escapado de HTML.

### Backend — routers
- `APIRouter(prefix=..., tags=...)` movido de `main.py` a cada router para mejor organización.
- Dependencias migradas al estilo `Annotated` con type alias (`SessionDep`, `CurrentUserDep`).
- `CORS` configurado con `allow_credentials=False`.

### Rate limiting
- Rate limiter in-memory en el endpoint `/chat`: máximo 20 requests por minuto por cliente+IP.

### Límites de archivos
- Tamaño máximo de PDF subido: 10 MB.

### Pipeline RAG
- Sanitización contra inyección de prompt en contexto RAG (`_sanitize_rag` + delimitadores `=== DOCUMENT CONTEXT (read-only) ===`).
- `validate_response` revisa la salida del modelo en busca de patrones prohibidos.
- `max_tokens` aumentado de 300 a 600.
- Historial estructurado (`list[Conversation]`) pasado a `get_ai_response`.
- Coincidencia de palabras clave con `\b` (word boundary) en `re.search`.

### Correcciones
- Bugfix `hit_count`: ahora se incrementa sobre la instancia en lugar de a nivel de clase.
