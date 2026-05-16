#!/usr/bin/env python3
"""Render the static eMule BB pages from Jinja2 templates and structured copy."""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape


SITE_BASE_URL = "https://emulebb.github.io"
PICO_CDN = "https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.classless.min.css"


@dataclass(frozen=True)
class PageSpec:
    """Static routing metadata for one generated page."""

    key: str
    hreflang: str
    html_lang: str
    directory: str
    priority: str
    language_label: str

    @property
    def output_path(self) -> Path:
        if self.directory:
            return Path(self.directory) / "index.html"
        return Path("index.html")

    @property
    def url(self) -> str:
        if self.directory:
            return f"{SITE_BASE_URL}/{self.directory}/"
        return f"{SITE_BASE_URL}/"

    @property
    def stylesheet_href(self) -> str:
        if self.directory:
            return "../styles.css"
        return "styles.css"


PAGES = (
    PageSpec("en", "en", "en", "", "1.0", "English"),
    PageSpec("es", "es", "es", "es", "0.8", "Español"),
    PageSpec("pt_br", "pt-BR", "pt-BR", "pt-br", "0.8", "Português (Brasil)"),
    PageSpec("pt_pt", "pt-PT", "pt-PT", "pt-pt", "0.8", "Português (Portugal)"),
    PageSpec("it", "it", "it", "it", "0.8", "Italiano"),
    PageSpec("ru", "ru", "ru", "ru", "0.8", "Русский"),
    PageSpec("de", "de", "de", "de", "0.8", "Deutsch"),
    PageSpec("fr", "fr", "fr", "fr", "0.8", "Français"),
    PageSpec("pl", "pl", "pl", "pl", "0.8", "Polski"),
    PageSpec("nl", "nl", "nl", "nl", "0.8", "Nederlands"),
    PageSpec("tr", "tr", "tr", "tr", "0.8", "Türkçe"),
)

DOCS = [
    ("https://github.com/eMulebb/eMule-tooling/blob/main/docs/reference/GUIDE-EMULEBB.md", "emulebb"),
    ("https://github.com/eMulebb/eMule-tooling/blob/main/docs/reference/GUIDE-SETUP.md", "setup"),
    ("https://github.com/eMulebb/eMule-tooling/blob/main/docs/reference/GUIDE-NETWORK.md", "network"),
    ("https://github.com/eMulebb/eMule-tooling/blob/main/docs/reference/GUIDE-SHARING.md", "sharing"),
    ("https://github.com/eMulebb/eMule-tooling/blob/main/docs/reference/GUIDE-DOWNLOADS-SEARCH.md", "downloads"),
    ("https://github.com/eMulebb/eMule-tooling/blob/main/docs/reference/GUIDE-CONTROLLERS-REST.md", "controllers"),
    ("https://github.com/eMulebb/eMule-tooling/blob/main/docs/rest/REST-API-CONTRACT.md", "rest_contract"),
    ("https://github.com/eMulebb/eMule-tooling/blob/main/docs/rest/REST-API-ADAPTERS.md", "rest_adapters"),
    ("https://github.com/eMulebb/eMule-tooling/blob/main/docs/reference/GUIDE-TROUBLESHOOTING.md", "troubleshooting"),
    ("https://github.com/eMulebb/eMule-tooling/blob/main/docs/active/RELEASE-0.7.3.md", "release"),
]

REPOS = [
    ("https://github.com/eMulebb/eMule", "emule"),
    ("https://github.com/eMulebb/eMulebb-setup", "setup"),
    ("https://github.com/eMulebb/eMule-build", "build"),
    ("https://github.com/eMulebb/eMule-build-tests", "tests"),
    ("https://github.com/eMulebb/eMule-tooling", "tooling"),
]


def c(span: str, h3: str, p: str) -> dict[str, str]:
    """Make a content card."""

    return {"span": span, "h3": h3, "p": p}


def s(eyebrow: str, h2: str, p: str = "") -> dict[str, Any]:
    """Make a section heading."""

    return {"eyebrow": eyebrow, "h2": h2, "p": p}


CONTENT: dict[str, dict[str, Any]] = {
    "en": {
        "title": "eMule broadband edition | eMule BB",
        "meta_description": "eMule broadband edition, or eMule BB, is a modern eMule build for broadband upload control, VPN/interface binding, improved performance defaults, large shared libraries, REST automation, eD2K, Kad, and power-user workflows.",
        "og_title": "eMule broadband edition | eMule BB",
        "og_description": "Modern eMule for broadband upload control, VPN/interface binding, improved performance defaults, large libraries, REST automation, eD2K/Kad compatibility, and release-grade validation. First public release 0.7.3 is planned and not yet released.",
        "structured_description": "Modern eMule for broadband upload control, VPN/interface binding, improved performance defaults, large shared libraries, REST automation, eD2K/Kad compatibility, and power-user workflows. The first public release is planned as 0.7.3 and is not yet released.",
        "nav_label": "Primary navigation",
        "project_links_label": "Project links",
        "product_summary_label": "eMule BB product summary",
        "footer_links_label": "Footer links",
        "nav": [
            {"id": "why", "label": "Why"},
            {"id": "features", "label": "Features"},
            {"id": "guide", "label": "Guide"},
            {"id": "docs", "label": "Docs"},
            {"id": "automation", "label": "Automation"},
            {"id": "release", "label": "Release"},
            {"id": "repos", "label": "Repos"},
        ],
        "hero": {
            "eyebrow": "Classic eMule, tuned for modern broadband",
            "h1": "eMule BB keeps eD2K and Kad useful for serious users.",
            "lead": "A power-user eMule for fast upload links, large shared libraries, always-on Windows sessions, and local controller workflows without abandoning the familiar desktop app.",
            "source": "Source",
            "guide": "Product guide",
            "panel_kicker": "Product posture",
            "panel_h2": "Conservative where compatibility matters. Modern where control matters.",
            "panel_p": "eMule BB keeps the native eMule workflow at the center and adds broadband-aware queue behavior, local API control, and release-grade validation around it.",
            "signals": ["Stock eD2K/Kad compatibility", "Broadband upload slot control", "VPN/interface binding", "Modern performance limits", "Authenticated JSON REST API", "Public 0.7.3 planned", "Release-grade validation workspace"],
        },
        "intro": "eMule broadband edition, compactly <strong>eMule BB</strong>, is an independent product line for people who still value eMule's distributed sharing model. It preserves the classic desktop workflows while making the client easier to run, observe, automate, and validate on current Windows systems.",
        "why": {
            **s("Why", "A legacy client is useful only if it can still be operated with confidence", "eMule BB is partly a product effort and partly a disciplined learning exercise: preserve a complex native Windows application with real network behavior, then surround it with modern build, test, documentation, automation, and release practice."),
            "cards": [
                c("Product reason", "Keep eD2K and Kad practical", "The goal is not nostalgia or a rewrite. It is to keep the classic sharing model usable for long sessions, rare files, deliberate seeding, and users who still want a native desktop client."),
                c("Engineering reason", "Move old assumptions into daylight", "Defaults around upload slots, timeouts, buffers, large libraries, and WebServer exposure are made explicit so each change can be reviewed, tested, documented, and adjusted."),
                c("Release reason", "Practice modern proof on legacy code", "The workspace treats release as an engineering artifact: source policy, OpenAPI contracts, reproducible builds, package hashes, live checks, and operator gates all have to line up."),
            ],
        },
        "features": {
            **s("Features", "What eMule BB adds around the classic client", "The work is focused on operator-visible behavior: predictable upload policy, safer binding, fixed performance limits, large-library operation, local automation, and release evidence for the planned <code>0.7.3</code> release."),
            "cards": [
                c("Sharing and upload", "Broadband upload control", "Bounded slot targets, weak-slot recycling, ratio readouts, and seeding controls keep fast upload links useful without changing the eD2K upload protocol."),
                c("Network control", "Binding, NAT, and exposure policy", "Interface-aware binding, UPnP/NAT mapping validation, HTTPS, allowed-IP rules, and WebServer inheritance keep remote surfaces explicit and testable."),
                c("Performance and scale", "Modern defaults for large sessions", "Higher socket buffers, queue/source limits, file buffering, timeout defaults, recursive share sync, and long-path guidance target current Windows systems and large libraries."),
                c("Classic network", "eD2K and Kad stay first", "Server, global, and Kad search remain the native foundation, with Kad identity tracking, bad-node handling, cleanup, and timing work kept inside compatibility boundaries."),
                c("Automation", "REST and controller workflows", "Authenticated JSON endpoints cover transfers, searches, shared files, servers, Kad, logs, categories, uploads, statistics, preferences, and controlled shutdown from trusted local tools."),
                c("Release discipline", "Evidence before public packages", "The planned <code>0.7.3</code> beta depends on native tests, REST contracts, live controller lanes, network adversity, packaging, and x64/ARM64 rehearsals."),
            ],
        },
        "guide": {
            **s("Product guide", "A short operating model"),
            "cards": [
                c("", "Start from known-good eMule habits", "Use trusted server lists, bootstrap Kad deliberately, keep incoming and shared directories predictable, and preserve the classic search/add/share workflow before layering automation on top."),
                c("", "Tune upload for your real link", "Set a finite upload limit, choose a realistic upload client target, and let the broadband policy favor fewer stronger slots instead of many low-rate sessions."),
                c("", "Curate large libraries", "Use long-path capable Windows setups, keep share roots clean, watch ratios, and treat rare files as deliberate publishing decisions."),
                c("", "Automate only on trusted networks", "Enable WebServer/REST with an API key, bind and firewall it carefully, and use controllers that respect native eMule transfer and delete semantics."),
                c("", "Track release readiness", "Treat the public branch as active pre-release work until the planned <code>0.7.3</code> gates, operator checks, and live E2E evidence say otherwise."),
                c("", "Use the docs for depth", "The homepage stays compact. The product guide, REST contract, broadband notes, and release documents live as Markdown in the public tooling repository."),
            ],
        },
        "docs": {
            **s("Read more", "Detailed guides and source documents"),
            "links": [],
        },
        "automation": {
            "eyebrow": "Controller surface",
            "h2": "REST automation without replacing the desktop app",
            "p": "The broadband release track exposes a resource-oriented <code>/api/v1</code> JSON API from the existing WebServer listener. It authenticates with <code>X-API-Key</code>, serves JSON envelopes, and keeps native eMule state changes marshaled through the app.",
            "pills_label": "REST API areas",
            "pills": ["Transfers", "Searches", "Servers", "Kad", "Shared files", "Uploads", "Categories", "Logs", "Statistics", "Preferences"],
        },
        "release": {
            **s("Release posture", "Public release 0.7.3 is planned, gated, and not yet released"),
            "cards": [
                c("", "Current status", "The first public release target is <code>0.7.3</code>. It is not yet released. Final proof is currently paused by operator direction, and public status stays tied to the active release docs."),
                c("", "Build and package proof", "Required proof covers workspace validation, Debug and Release x64 app builds, Release ARM64 app builds, test binaries, package generation, clean-worktree checks, and recorded SHA-256 hashes."),
                c("", "Behavior proof", "Test gates cover native suites, REST contract and OpenAPI drift, malformed requests, UI automation, live controller-surface E2E, full Release x64 live E2E, and network-adversity scenarios."),
                c("", "Controller proof", "aMuTorrent, Prowlarr, Radarr, Sonarr, and qBittorrent-compatible adapter lanes prove that automation works without weakening the native <code>/api/v1</code> contract."),
                c("", "Compatibility proof", "Stock eD2K/Kad behavior remains the default. Broadband, REST, and controller features are added around that compatibility goal and compared against the community baseline where useful."),
            ],
        },
        "method": {
            **s("Implementation method", "Modernize around the legacy core, then prove the result", "The implementation style is intentionally conservative. eMule BB changes local policy, limits, diagnostics, API boundaries, and release discipline while keeping stock eD2K/Kad compatibility as the default."),
            "cards": [
                c("Compatibility", "No casual protocol drift", "Kad and eD2K changes stay inside local routing, timing, validation, and control paths. Wire formats, opcodes, and native desktop workflows remain compatibility boundaries."),
                c("Limits", "Fixed, reviewable defaults", "Modern bandwidth, memory, socket, queue, and timeout assumptions are expressed as explicit defaults or advanced preferences instead of hidden adaptive behavior."),
                c("REST", "Controller contracts, not screen scraping", "The authenticated JSON API follows an OpenAPI-backed contract, rejects malformed inputs, and marshals native state mutations through the app where the desktop client owns that state."),
                c("Release", "Evidence before labels", "The release process records commands, commits, logs, package paths, hashes, live evidence, and operator decisions so a release tag is a checked outcome."),
            ],
        },
        "repos": {**s("Public workspace", "Primary repositories"), "links": []},
        "team": {
            **s("Project lore", "The people keeping the queue from becoming performance art"),
            "cards": [
                c("", "Upload Slot Therapist", "Helps underperforming slots process their feelings for exactly long enough before escorting them back to the queue with a clipboard and a cooldown."),
                c("", "Kad Bootstrap Archivist", "Maintains the sacred list of nodes that worked once in 2007 and therefore deserve a respectful, heavily validated second chance."),
                c("", "Release Gate Bouncer", "Lets builds into the room only after they bring tests, live evidence, and a convincing explanation for what happened to the last socket."),
            ],
        },
    },
}


def clone_base(key: str, overrides: dict[str, Any]) -> dict[str, Any]:
    """Create a localized content dictionary from explicit localized sections."""

    merged = dict(CONTENT["en"])
    merged.update(overrides)
    return merged


CONTENT.update(
    {
        "es": clone_base(
            "es",
            {
                "title": "eMule broadband edition | eMule BB en español",
                "meta_description": "eMule BB es una edición moderna de eMule para controlar uploads en banda ancha, VPN/interface binding, mejores límites de rendimiento, bibliotecas compartidas grandes, REST automation, eD2K, Kad y workflows avanzados.",
                "og_title": "eMule broadband edition | eMule BB en español",
                "og_description": "eMule moderno para controlar uploads en banda ancha, VPN/interface binding, límites de rendimiento actuales, bibliotecas grandes, REST automation, compatibilidad eD2K/Kad y validación de release. La primera versión pública 0.7.3 está planificada y aún no se ha publicado.",
                "structured_description": "eMule moderno para controlar uploads en banda ancha, VPN/interface binding, límites de rendimiento actuales, bibliotecas compartidas grandes, REST automation, compatibilidad eD2K/Kad y workflows avanzados. La primera versión pública está planificada como 0.7.3 y aún no se ha publicado.",
                "nav_label": "Navegación principal",
                "project_links_label": "Enlaces del proyecto",
                "product_summary_label": "Resumen de eMule BB",
                "footer_links_label": "Enlaces del pie",
                "nav": [{"id": "why", "label": "Por qué"}, {"id": "features", "label": "Funciones"}, {"id": "guide", "label": "Guía"}, {"id": "docs", "label": "Documentación"}, {"id": "automation", "label": "Automatización"}, {"id": "release", "label": "Lanzamiento"}, {"id": "repos", "label": "Repositorios"}],
                "hero": {"eyebrow": "El eMule clásico, ajustado para la banda ancha actual", "h1": "eMule BB mantiene eD2K y Kad útiles para usuarios exigentes.", "lead": "Un eMule para usuarios avanzados con enlaces de upload rápidos, bibliotecas compartidas grandes, sesiones de Windows siempre activas y workflows locales de control sin abandonar la aplicación de escritorio conocida.", "source": "Código fuente", "guide": "Guía del producto", "panel_kicker": "Enfoque del producto", "panel_h2": "Conservador donde importa la compatibilidad. Moderno donde importa el control.", "panel_p": "eMule BB mantiene el workflow nativo de eMule en el centro y añade colas pensadas para banda ancha, control local por API y validación de release a su alrededor.", "signals": ["Compatibilidad eD2K/Kad de serie", "Control de slots de upload en banda ancha", "VPN/interface binding", "Límites de rendimiento actuales", "JSON REST API autenticada", "0.7.3 pública planificada", "Workspace de validación de release"]},
                "intro": "eMule broadband edition, en corto <strong>eMule BB</strong>, es una línea de producto independiente para quienes todavía valoran el modelo distribuido de eMule. Conserva los workflows clásicos de escritorio y hace que el cliente sea más fácil de ejecutar, observar, automatizar y validar en sistemas Windows actuales.",
                "why": {**s("Por qué", "Un cliente legado solo sirve si todavía puede operarse con confianza", "eMule BB es a la vez producto y ejercicio de ingeniería disciplinada: conservar una aplicación nativa de Windows con comportamiento real de red y rodearla de build, pruebas, documentación, automatización y proceso de release modernos."), "cards": [c("Motivo de producto", "Mantener eD2K y Kad prácticos", "El objetivo no es la nostalgia ni una reescritura. Es mantener útil el modelo clásico para sesiones largas, archivos raros, seeding deliberado y usuarios que aún quieren un cliente nativo."), c("Motivo técnico", "Poner los supuestos antiguos a la vista", "Los valores por defecto de slots de upload, timeouts, buffers, bibliotecas grandes y exposición de WebServer quedan explícitos para poder revisarlos, probarlos y documentarlos."), c("Motivo de release", "Probar código legado con métodos actuales", "El workspace trata el release como un artefacto de ingeniería: política de fuentes, contratos OpenAPI, builds reproducibles, hashes, pruebas live y gates de operador deben coincidir.")]},
                "features": {**s("Funciones", "Lo que eMule BB añade alrededor del cliente clásico", "El trabajo se centra en comportamiento visible para el operador: política de upload predecible, binding más seguro, límites fijos de rendimiento, bibliotecas grandes, automatización local y evidencia para el release planificado <code>0.7.3</code>."), "cards": [c("Compartir y upload", "Control de upload en banda ancha", "Objetivos acotados de slots, reciclaje de slots débiles, ratios visibles y controles de seeding mantienen útiles los enlaces rápidos sin cambiar el protocolo de upload eD2K."), c("Control de red", "Binding, NAT y exposición", "Interface-aware binding, validación UPnP/NAT, HTTPS, reglas de IP permitida y herencia de WebServer mantienen las superficies remotas explícitas y comprobables."), c("Rendimiento y escala", "Valores actuales para sesiones grandes", "Buffers de socket mayores, límites de queue/source, file buffering, timeouts, sync recursiva y guía de long paths apuntan a Windows actuales y bibliotecas grandes."), c("Red clásica", "eD2K y Kad siguen primero", "Las búsquedas Server, global y Kad siguen siendo la base, con identidad Kad, manejo de nodos malos, limpieza y timing dentro de límites compatibles."), c("Automatización", "REST y workflows de control", "Endpoints JSON autenticados cubren transferencias, búsquedas, archivos compartidos, servidores, Kad, logs, categorías, uploads, estadísticas, preferencias y apagado controlado."), c("Disciplina de release", "Evidencia antes de paquetes públicos", "La beta <code>0.7.3</code> depende de pruebas nativas, contratos REST, carriles live de controladores, adversidad de red, packaging y ensayos x64/ARM64.")]},
                "guide": {**s("Guía del producto", "Un modelo breve de operación"), "cards": [c("", "Partir de buenos hábitos de eMule", "Usa listas de servidores fiables, arranca Kad con intención, mantén predecibles las carpetas incoming y compartidas, y conserva el workflow clásico antes de añadir automatización."), c("", "Ajustar el upload al enlace real", "Define un límite de upload finito, elige un objetivo realista de clientes y deja que la política de banda ancha favorezca menos slots, pero más fuertes."), c("", "Cuidar bibliotecas grandes", "Usa Windows con long paths, mantén limpias las raíces compartidas, vigila ratios y trata los archivos raros como decisiones deliberadas de publicación."), c("", "Automatizar solo en redes confiables", "Activa WebServer/REST con API key, aplica binding y firewall con cuidado, y usa controladores que respeten la semántica nativa de eMule."), c("", "Seguir la preparación del release", "Trata la rama pública como pre-release activo hasta que los gates <code>0.7.3</code>, las comprobaciones de operador y la evidencia live E2E indiquen lo contrario."), c("", "Usar la documentación para profundizar", "La página principal es compacta. La guía de producto, el contrato REST, las notas de banda ancha y los documentos de release viven como Markdown en el repositorio de tooling.")]},
                "automation": {"eyebrow": "Superficie de control", "h2": "REST automation sin reemplazar la aplicación de escritorio", "p": "La línea de release de banda ancha expone una JSON API <code>/api/v1</code> orientada a recursos desde el listener WebServer existente. Autentica con <code>X-API-Key</code>, sirve envoltorios JSON y mantiene los cambios de estado de eMule canalizados por la aplicación.", "pills_label": "Áreas de REST API", "pills": ["Transferencias", "Búsquedas", "Servidores", "Kad", "Archivos compartidos", "Uploads", "Categorías", "Logs", "Estadísticas", "Preferencias"]},
                "release": {**s("Estado del release", "La versión pública 0.7.3 está planificada, tiene gates y aún no se ha publicado"), "cards": [c("", "Estado actual", "El primer objetivo público es <code>0.7.3</code>. Aún no se ha publicado. La prueba final está pausada por dirección del operador y el estado público sigue ligado a los documentos activos."), c("", "Prueba de build y paquete", "La evidencia requerida cubre validación del workspace, builds Debug y Release x64, builds Release ARM64, binarios de prueba, paquetes, worktree limpio y hashes SHA-256."), c("", "Prueba de comportamiento", "Los gates cubren suites nativas, contrato REST, drift OpenAPI, requests malformados, automatización UI, E2E live de controladores, Release x64 live E2E completo y adversidad de red."), c("", "Prueba de controladores", "aMuTorrent, Prowlarr, Radarr, Sonarr y carriles compatibles con qBittorrent prueban automatización sin debilitar el contrato nativo <code>/api/v1</code>."), c("", "Prueba de compatibilidad", "El comportamiento eD2K/Kad de serie sigue siendo el valor por defecto. Banda ancha, REST y controladores se añaden alrededor de ese objetivo de compatibilidad.")]},
                "method": {**s("Método de implementación", "Modernizar alrededor del núcleo legado y después probar el resultado", "El estilo es deliberadamente conservador. eMule BB cambia política local, límites, diagnósticos, límites de API y disciplina de release, manteniendo la compatibilidad eD2K/Kad como valor por defecto."), "cards": [c("Compatibilidad", "Sin drift casual del protocolo", "Los cambios Kad y eD2K se mantienen en rutas locales, timing, validación y control. Formatos wire, opcodes y workflows nativos son límites de compatibilidad."), c("Límites", "Valores fijos y revisables", "Los supuestos modernos de bandwidth, memoria, socket, queue y timeout se expresan como defaults explícitos o preferencias avanzadas."), c("REST", "Contratos de control, no screen scraping", "La JSON API autenticada sigue un contrato OpenAPI, rechaza entradas malformadas y canaliza mutaciones nativas por la aplicación."), c("Release", "Evidencia antes que etiquetas", "El proceso registra comandos, commits, logs, rutas de paquetes, hashes, evidencia live y decisiones de operador para que el tag sea un resultado comprobado.")]},
                "repos": {**s("Workspace público", "Repositorios principales"), "links": []},
                "team": {**s("Cultura del proyecto", "La gente que evita que la queue se vuelva teatro de rendimiento"), "cards": [c("", "Terapeuta de slots de upload", "Ayuda a los slots flojos a procesar sus sentimientos el tiempo justo antes de devolverlos a la queue con formulario y cooldown."), c("", "Archivista de bootstrap Kad", "Conserva la lista sagrada de nodos que funcionaron una vez en 2007 y merecen una segunda oportunidad, bien validada."), c("", "Portero de gates de release", "Deja entrar builds solo si traen pruebas, evidencia live y una explicación convincente sobre el último socket.")]},
            },
        ),
        "pt_br": clone_base(
            "pt_br",
            {
                "title": "eMule broadband edition | eMule BB em português do Brasil",
                "meta_description": "eMule BB é uma edição moderna do eMule para controle de upload em banda larga, VPN/interface binding, limites de desempenho atuais, grandes bibliotecas compartilhadas, REST automation, eD2K, Kad e workflows avançados.",
                "og_title": "eMule broadband edition | eMule BB em português do Brasil",
                "og_description": "eMule moderno para controle de upload em banda larga, VPN/interface binding, limites de desempenho atuais, bibliotecas grandes, REST automation, compatibilidade eD2K/Kad e validação de release. A primeira versão pública 0.7.3 está planejada e ainda não foi lançada.",
                "structured_description": "eMule moderno para controle de upload em banda larga, VPN/interface binding, limites de desempenho atuais, grandes bibliotecas compartilhadas, REST automation, compatibilidade eD2K/Kad e workflows avançados. A primeira versão pública está planejada como 0.7.3 e ainda não foi lançada.",
                "nav_label": "Navegação principal",
                "project_links_label": "Links do projeto",
                "product_summary_label": "Resumo do eMule BB",
                "footer_links_label": "Links do rodapé",
                "nav": [{"id": "why", "label": "Por quê"}, {"id": "features", "label": "Recursos"}, {"id": "guide", "label": "Guia"}, {"id": "docs", "label": "Documentação"}, {"id": "automation", "label": "Automação"}, {"id": "release", "label": "Lançamento"}, {"id": "repos", "label": "Repositórios"}],
                "hero": {"eyebrow": "O eMule clássico, ajustado para a banda larga atual", "h1": "eMule BB mantém eD2K e Kad úteis para usuários exigentes.", "lead": "Um eMule para usuários avançados, com links de upload rápidos, grandes bibliotecas compartilhadas, sessões Windows sempre ativas e workflows locais de controle sem abandonar o aplicativo desktop conhecido.", "source": "Código-fonte", "guide": "Guia do produto", "panel_kicker": "Postura do produto", "panel_h2": "Conservador onde a compatibilidade importa. Moderno onde o controle importa.", "panel_p": "eMule BB mantém o workflow nativo do eMule no centro e adiciona filas preparadas para banda larga, controle local por API e validação de release ao redor dele.", "signals": ["Compatibilidade eD2K/Kad original", "Controle de slots de upload em banda larga", "VPN/interface binding", "Limites de desempenho atuais", "JSON REST API autenticada", "0.7.3 pública planejada", "Workspace de validação de release"]},
                "intro": "eMule broadband edition, ou simplesmente <strong>eMule BB</strong>, é uma linha de produto independente para quem ainda valoriza o modelo distribuído do eMule. Ele preserva os workflows clássicos do desktop e torna o cliente mais fácil de executar, observar, automatizar e validar em sistemas Windows atuais.",
                "why": {**s("Por quê", "Um cliente legado só é útil se ainda puder ser operado com confiança", "eMule BB é produto e também disciplina de engenharia: preservar uma aplicação nativa Windows com comportamento real de rede e cercá-la de build, testes, documentação, automação e processo de release modernos."), "cards": [c("Motivo de produto", "Manter eD2K e Kad práticos", "A meta não é nostalgia nem reescrita. É manter o modelo clássico útil para sessões longas, arquivos raros, seeding deliberado e usuários que ainda querem um cliente nativo."), c("Motivo técnico", "Tornar explícitas as suposições antigas", "Defaults de slots de upload, timeouts, buffers, bibliotecas grandes e exposição do WebServer ficam visíveis para revisão, teste e documentação."), c("Motivo de release", "Aplicar prova moderna a código legado", "O workspace trata release como artefato de engenharia: política de fonte, contratos OpenAPI, builds reproduzíveis, hashes, checks live e gates de operador precisam fechar.")]},
                "features": {**s("Recursos", "O que eMule BB adiciona ao redor do cliente clássico", "O foco está no comportamento visível para o operador: política de upload previsível, binding mais seguro, limites fixos de desempenho, bibliotecas grandes, automação local e evidência para o release planejado <code>0.7.3</code>."), "cards": [c("Compartilhamento e upload", "Controle de upload em banda larga", "Metas limitadas de slots, reciclagem de slots fracos, leitura de ratios e controles de seeding mantêm links rápidos úteis sem alterar o protocolo de upload eD2K."), c("Controle de rede", "Binding, NAT e política de exposição", "Interface-aware binding, validação UPnP/NAT, HTTPS, regras de IP permitido e herança do WebServer mantêm superfícies remotas explícitas e testáveis."), c("Desempenho e escala", "Defaults atuais para sessões grandes", "Buffers maiores, limites de queue/source, file buffering, timeouts, sync recursiva e orientação de long paths miram Windows atuais e bibliotecas grandes."), c("Rede clássica", "eD2K e Kad continuam em primeiro lugar", "Busca Server, global e Kad seguem como base nativa, com identidade Kad, tratamento de nós ruins, limpeza e timing dentro de limites compatíveis."), c("Automação", "REST e workflows de controle", "Endpoints JSON autenticados cobrem transferências, buscas, arquivos compartilhados, servidores, Kad, logs, categorias, uploads, estatísticas, preferências e shutdown controlado."), c("Disciplina de release", "Evidência antes de pacotes públicos", "A beta <code>0.7.3</code> depende de testes nativos, contratos REST, lanes live de controladores, adversidade de rede, packaging e ensaios x64/ARM64.")]},
                "guide": {**s("Guia do produto", "Um modelo curto de operação"), "cards": [c("", "Comece por bons hábitos do eMule", "Use listas confiáveis de servidores, inicialize Kad com cuidado, mantenha pastas incoming e compartilhadas previsíveis e preserve o workflow clássico antes da automação."), c("", "Ajuste o upload ao seu link real", "Defina um limite finito de upload, escolha uma meta realista de clientes e deixe a política de banda larga favorecer menos slots, porém mais fortes."), c("", "Cuide de bibliotecas grandes", "Use Windows com long paths, mantenha raízes de compartilhamento limpas, acompanhe ratios e trate arquivos raros como decisões deliberadas de publicação."), c("", "Automatize só em redes confiáveis", "Ative WebServer/REST com API key, aplique binding e firewall com cuidado e use controladores que respeitem a semântica nativa do eMule."), c("", "Acompanhe a prontidão do release", "Trate a branch pública como pre-release ativo até que os gates <code>0.7.3</code>, checks do operador e evidência live E2E digam o contrário."), c("", "Use a documentação para detalhes", "A página principal é compacta. Guia do produto, contrato REST, notas de banda larga e documentos de release vivem como Markdown no repositório de tooling.")]},
                "automation": {"eyebrow": "Superfície de controle", "h2": "REST automation sem substituir o aplicativo desktop", "p": "A linha de release de banda larga expõe uma JSON API <code>/api/v1</code> orientada a recursos a partir do listener WebServer existente. Ela autentica com <code>X-API-Key</code>, entrega envelopes JSON e mantém mudanças de estado do eMule mediadas pelo aplicativo.", "pills_label": "Áreas da REST API", "pills": ["Transferências", "Buscas", "Servidores", "Kad", "Arquivos compartilhados", "Uploads", "Categorias", "Logs", "Estatísticas", "Preferências"]},
                "release": {**s("Estado do release", "A versão pública 0.7.3 está planejada, tem gates e ainda não foi lançada"), "cards": [c("", "Estado atual", "O primeiro alvo público é <code>0.7.3</code>. Ele ainda não foi lançado. A prova final está pausada por direção do operador e o status público segue os documentos ativos."), c("", "Prova de build e pacote", "A prova cobre validação do workspace, builds Debug e Release x64, builds Release ARM64, binários de teste, geração de pacote, worktree limpo e hashes SHA-256."), c("", "Prova de comportamento", "Os gates cobrem suites nativas, contrato REST, drift OpenAPI, requests malformados, automação UI, E2E live de controladores, Release x64 live E2E completo e adversidade de rede."), c("", "Prova de controladores", "aMuTorrent, Prowlarr, Radarr, Sonarr e lanes compatíveis com qBittorrent provam automação sem enfraquecer o contrato nativo <code>/api/v1</code>."), c("", "Prova de compatibilidade", "O comportamento eD2K/Kad original permanece default. Banda larga, REST e controladores são adicionados ao redor desse objetivo de compatibilidade.")]},
                "method": {**s("Método de implementação", "Modernizar ao redor do núcleo legado e então provar o resultado", "O estilo é deliberadamente conservador. eMule BB muda política local, limites, diagnósticos, limites de API e disciplina de release mantendo compatibilidade eD2K/Kad como default."), "cards": [c("Compatibilidade", "Sem drift casual de protocolo", "Mudanças Kad e eD2K ficam em rotas locais, timing, validação e controle. Wire formats, opcodes e workflows nativos são limites de compatibilidade."), c("Limites", "Defaults fixos e revisáveis", "Suposições modernas de bandwidth, memória, socket, queue e timeout aparecem como defaults explícitos ou preferências avançadas."), c("REST", "Contratos de controle, não screen scraping", "A JSON API autenticada segue contrato OpenAPI, rejeita entradas malformadas e encaminha mutações nativas pelo aplicativo."), c("Release", "Evidência antes de etiquetas", "O processo registra comandos, commits, logs, caminhos de pacote, hashes, evidência live e decisões do operador para que o tag seja um resultado verificado.")]},
                "repos": {**s("Workspace público", "Repositórios principais"), "links": []},
                "team": {**s("Cultura do projeto", "A equipe que impede a queue de virar arte performática"), "cards": [c("", "Terapeuta de slots de upload", "Ajuda slots fracos a processar seus sentimentos pelo tempo exato antes de devolvê-los à queue com prancheta e cooldown."), c("", "Arquivista de bootstrap Kad", "Mantém a lista sagrada de nós que funcionaram uma vez em 2007 e merecem uma segunda chance bem validada."), c("", "Porteiro dos gates de release", "Só deixa builds entrarem se trouxerem testes, evidência live e uma boa explicação sobre o último socket.")]},
            },
        ),
        "pt_pt": clone_base(
            "pt_pt",
            {
                "title": "eMule broadband edition | eMule BB em português europeu",
                "meta_description": "eMule BB é uma edição moderna do eMule para controlo de upload em banda larga, VPN/interface binding, limites de desempenho actuais, grandes bibliotecas partilhadas, REST automation, eD2K, Kad e workflows avançados.",
                "og_title": "eMule broadband edition | eMule BB em português europeu",
                "og_description": "eMule moderno para controlo de upload em banda larga, VPN/interface binding, limites de desempenho actuais, bibliotecas grandes, REST automation, compatibilidade eD2K/Kad e validação de release. A primeira versão pública 0.7.3 está planeada e ainda não foi lançada.",
                "structured_description": "eMule moderno para controlo de upload em banda larga, VPN/interface binding, limites de desempenho actuais, grandes bibliotecas partilhadas, REST automation, compatibilidade eD2K/Kad e workflows avançados. A primeira versão pública está planeada como 0.7.3 e ainda não foi lançada.",
                "nav_label": "Navegação principal",
                "project_links_label": "Ligações do projecto",
                "product_summary_label": "Resumo do eMule BB",
                "footer_links_label": "Ligações do rodapé",
                "nav": [{"id": "why", "label": "Porquê"}, {"id": "features", "label": "Funcionalidades"}, {"id": "guide", "label": "Guia"}, {"id": "docs", "label": "Documentação"}, {"id": "automation", "label": "Automação"}, {"id": "release", "label": "Lançamento"}, {"id": "repos", "label": "Repositórios"}],
                "hero": {"eyebrow": "O eMule clássico, afinado para a banda larga actual", "h1": "eMule BB mantém eD2K e Kad úteis para utilizadores exigentes.", "lead": "Um eMule para utilizadores avançados, com uploads rápidos, grandes bibliotecas partilhadas, sessões Windows sempre activas e workflows locais de controlo sem abandonar a aplicação desktop conhecida.", "source": "Código-fonte", "guide": "Guia do produto", "panel_kicker": "Postura do produto", "panel_h2": "Conservador onde a compatibilidade importa. Moderno onde o controlo importa.", "panel_p": "eMule BB mantém o workflow nativo do eMule no centro e acrescenta filas preparadas para banda larga, controlo local por API e validação de release à sua volta.", "signals": ["Compatibilidade eD2K/Kad original", "Controlo de slots de upload em banda larga", "VPN/interface binding", "Limites de desempenho actuais", "JSON REST API autenticada", "0.7.3 pública planeada", "Workspace de validação de release"]},
                "intro": "eMule broadband edition, ou simplesmente <strong>eMule BB</strong>, é uma linha de produto independente para quem ainda valoriza o modelo distribuído do eMule. Preserva os workflows clássicos de desktop e torna o cliente mais fácil de executar, observar, automatizar e validar em sistemas Windows actuais.",
                "why": {**s("Porquê", "Um cliente legado só é útil se ainda puder ser operado com confiança", "eMule BB é produto e também disciplina de engenharia: preservar uma aplicação nativa Windows com comportamento real de rede e rodeá-la de build, testes, documentação, automação e processo de release modernos."), "cards": [c("Motivo de produto", "Manter eD2K e Kad práticos", "A meta não é nostalgia nem reescrita. É manter o modelo clássico útil para sessões longas, ficheiros raros, seeding deliberado e utilizadores que ainda querem um cliente nativo."), c("Motivo técnico", "Tornar explícitas as suposições antigas", "Defaults de slots de upload, timeouts, buffers, bibliotecas grandes e exposição do WebServer ficam visíveis para revisão, teste e documentação."), c("Motivo de release", "Aplicar prova moderna a código legado", "O workspace trata release como artefacto de engenharia: política de fonte, contratos OpenAPI, builds reproduzíveis, hashes, checks live e gates de operador precisam de fechar.")]},
                "features": {**s("Funcionalidades", "O que eMule BB acrescenta ao cliente clássico", "O foco está no comportamento visível para o operador: política de upload previsível, binding mais seguro, limites fixos de desempenho, bibliotecas grandes, automação local e evidência para o release planeado <code>0.7.3</code>."), "cards": [c("Partilha e upload", "Controlo de upload em banda larga", "Metas limitadas de slots, reciclagem de slots fracos, leitura de ratios e controlos de seeding mantêm ligações rápidas úteis sem alterar o protocolo de upload eD2K."), c("Controlo de rede", "Binding, NAT e política de exposição", "Interface-aware binding, validação UPnP/NAT, HTTPS, regras de IP permitido e herança do WebServer mantêm superfícies remotas explícitas e testáveis."), c("Desempenho e escala", "Defaults actuais para sessões grandes", "Buffers maiores, limites de queue/source, file buffering, timeouts, sync recursiva e orientação de long paths visam Windows actuais e bibliotecas grandes."), c("Rede clássica", "eD2K e Kad continuam em primeiro lugar", "Pesquisa Server, global e Kad seguem como base nativa, com identidade Kad, tratamento de nós maus, limpeza e timing dentro de limites compatíveis."), c("Automação", "REST e workflows de controlo", "Endpoints JSON autenticados cobrem transferências, pesquisas, ficheiros partilhados, servidores, Kad, logs, categorias, uploads, estatísticas, preferências e shutdown controlado."), c("Disciplina de release", "Evidência antes de pacotes públicos", "A beta <code>0.7.3</code> depende de testes nativos, contratos REST, lanes live de controladores, adversidade de rede, packaging e ensaios x64/ARM64.")]},
                "guide": {**s("Guia do produto", "Um modelo curto de operação"), "cards": [c("", "Começar por bons hábitos do eMule", "Usa listas fiáveis de servidores, inicializa Kad com cuidado, mantém pastas incoming e partilhadas previsíveis e preserva o workflow clássico antes da automação."), c("", "Ajustar o upload à ligação real", "Define um limite finito de upload, escolhe uma meta realista de clientes e deixa a política de banda larga favorecer menos slots, mas mais fortes."), c("", "Cuidar de bibliotecas grandes", "Usa Windows com long paths, mantém raízes de partilha limpas, acompanha ratios e trata ficheiros raros como decisões deliberadas de publicação."), c("", "Automatizar só em redes fiáveis", "Activa WebServer/REST com API key, aplica binding e firewall com cuidado e usa controladores que respeitem a semântica nativa do eMule."), c("", "Acompanhar a prontidão do release", "Trata a branch pública como pre-release activo até que os gates <code>0.7.3</code>, checks do operador e evidência live E2E indiquem o contrário."), c("", "Usar a documentação para detalhe", "A página principal é compacta. Guia do produto, contrato REST, notas de banda larga e documentos de release vivem como Markdown no repositório de tooling.")]},
                "automation": {"eyebrow": "Superfície de controlo", "h2": "REST automation sem substituir a aplicação desktop", "p": "A linha de release de banda larga expõe uma JSON API <code>/api/v1</code> orientada a recursos a partir do listener WebServer existente. Autentica com <code>X-API-Key</code>, entrega envelopes JSON e mantém alterações de estado do eMule mediadas pela aplicação.", "pills_label": "Áreas da REST API", "pills": ["Transferências", "Pesquisas", "Servidores", "Kad", "Ficheiros partilhados", "Uploads", "Categorias", "Logs", "Estatísticas", "Preferências"]},
                "release": {**s("Estado do release", "A versão pública 0.7.3 está planeada, tem gates e ainda não foi lançada"), "cards": [c("", "Estado actual", "O primeiro alvo público é <code>0.7.3</code>. Ainda não foi lançado. A prova final está pausada por orientação do operador e o estado público segue os documentos activos."), c("", "Prova de build e pacote", "A prova cobre validação do workspace, builds Debug e Release x64, builds Release ARM64, binários de teste, geração de pacote, worktree limpa e hashes SHA-256."), c("", "Prova de comportamento", "Os gates cobrem suites nativas, contrato REST, drift OpenAPI, requests malformados, automação UI, E2E live de controladores, Release x64 live E2E completo e adversidade de rede."), c("", "Prova de controladores", "aMuTorrent, Prowlarr, Radarr, Sonarr e lanes compatíveis com qBittorrent provam automação sem enfraquecer o contrato nativo <code>/api/v1</code>."), c("", "Prova de compatibilidade", "O comportamento eD2K/Kad original permanece default. Banda larga, REST e controladores são acrescentados à volta desse objectivo de compatibilidade.")]},
                "method": {**s("Método de implementação", "Modernizar à volta do núcleo legado e depois provar o resultado", "O estilo é deliberadamente conservador. eMule BB muda política local, limites, diagnósticos, limites de API e disciplina de release mantendo compatibilidade eD2K/Kad como default."), "cards": [c("Compatibilidade", "Sem drift casual de protocolo", "Mudanças Kad e eD2K ficam em rotas locais, timing, validação e controlo. Wire formats, opcodes e workflows nativos são limites de compatibilidade."), c("Limites", "Defaults fixos e revistos", "Suposições modernas de bandwidth, memória, socket, queue e timeout aparecem como defaults explícitos ou preferências avançadas."), c("REST", "Contratos de controlo, não screen scraping", "A JSON API autenticada segue contrato OpenAPI, rejeita entradas malformadas e encaminha mutações nativas pela aplicação."), c("Release", "Evidência antes de etiquetas", "O processo regista comandos, commits, logs, caminhos de pacote, hashes, evidência live e decisões do operador para que o tag seja um resultado verificado.")]},
                "repos": {**s("Workspace público", "Repositórios principais"), "links": []},
                "team": {**s("Cultura do projecto", "A equipa que impede a queue de virar teatro de desempenho"), "cards": [c("", "Terapeuta de slots de upload", "Ajuda slots fracos a processar os sentimentos pelo tempo exacto antes de os devolver à queue com prancheta e cooldown."), c("", "Arquivista de bootstrap Kad", "Mantém a lista sagrada de nós que funcionaram uma vez em 2007 e merecem uma segunda oportunidade bem validada."), c("", "Porteiro dos gates de release", "Só deixa builds entrar se trouxerem testes, evidência live e uma boa explicação sobre o último socket.")]},
            },
        ),
        "it": clone_base(
            "it",
            {
                "title": "eMule broadband edition | eMule BB in italiano",
                "meta_description": "eMule BB è una edizione moderna di eMule per controllo upload su banda larga, VPN/interface binding, limiti di prestazione attuali, grandi librerie condivise, REST automation, eD2K, Kad e workflow avanzati.",
                "og_title": "eMule broadband edition | eMule BB in italiano",
                "og_description": "eMule moderno per controllo upload su banda larga, VPN/interface binding, limiti di prestazione attuali, grandi librerie, REST automation, compatibilità eD2K/Kad e validazione di release. La prima versione pubblica 0.7.3 è pianificata e non è ancora uscita.",
                "structured_description": "eMule moderno per controllo upload su banda larga, VPN/interface binding, limiti di prestazione attuali, grandi librerie condivise, REST automation, compatibilità eD2K/Kad e workflow avanzati. La prima versione pubblica è pianificata come 0.7.3 e non è ancora uscita.",
                "nav_label": "Navigazione principale",
                "project_links_label": "Link del progetto",
                "product_summary_label": "Sintesi di eMule BB",
                "footer_links_label": "Link di fondo pagina",
                "nav": [{"id": "why", "label": "Perché"}, {"id": "features", "label": "Funzioni"}, {"id": "guide", "label": "Guida"}, {"id": "docs", "label": "Documentazione"}, {"id": "automation", "label": "Automazione"}, {"id": "release", "label": "Rilascio"}, {"id": "repos", "label": "Repository"}],
                "hero": {"eyebrow": "Il classico eMule, tarato per la banda larga attuale", "h1": "eMule BB mantiene eD2K e Kad utili per utenti esigenti.", "lead": "Un eMule per power user con upload veloci, grandi librerie condivise, sessioni Windows sempre attive e workflow locali di controllo senza abbandonare la familiare app desktop.", "source": "Codice sorgente", "guide": "Guida prodotto", "panel_kicker": "Posizionamento", "panel_h2": "Conservativo dove conta la compatibilità. Moderno dove conta il controllo.", "panel_p": "eMule BB mantiene al centro il workflow nativo di eMule e vi aggiunge code adatte alla banda larga, controllo locale via API e validazione di release.", "signals": ["Compatibilità eD2K/Kad originale", "Controllo degli upload slot", "VPN/interface binding", "Limiti di prestazione attuali", "JSON REST API autenticata", "0.7.3 pubblica pianificata", "Workspace di validazione release"]},
                "intro": "eMule broadband edition, in breve <strong>eMule BB</strong>, è una linea di prodotto indipendente per chi dà ancora valore al modello distribuito di eMule. Conserva i workflow desktop classici e rende il client più semplice da eseguire, osservare, automatizzare e validare sui sistemi Windows attuali.",
                "why": {**s("Perché", "Un client legacy è utile solo se può ancora essere gestito con fiducia", "eMule BB è insieme prodotto e disciplina tecnica: preservare una applicazione nativa Windows con vero comportamento di rete e circondarla di build, test, documentazione, automazione e processo di release moderni."), "cards": [c("Motivo di prodotto", "Tenere pratici eD2K e Kad", "Non è nostalgia e non è una riscrittura. Serve a mantenere utile il modello classico per sessioni lunghe, file rari, seeding deliberato e utenti che vogliono ancora un client nativo."), c("Motivo tecnico", "Rendere visibili le vecchie ipotesi", "Default per upload slot, timeout, buffer, grandi librerie ed esposizione WebServer diventano espliciti, quindi revisionabili, testabili e documentabili."), c("Motivo di release", "Applicare prove moderne a codice legacy", "Il workspace tratta la release come un artefatto tecnico: policy del sorgente, contratti OpenAPI, build riproducibili, hash, controlli live e gate operatore devono combaciare.")]},
                "features": {**s("Funzioni", "Cosa aggiunge eMule BB intorno al client classico", "Il lavoro punta a comportamento visibile all'operatore: upload prevedibile, binding più sicuro, limiti fissi di prestazione, grandi librerie, automazione locale ed evidenza per la release pianificata <code>0.7.3</code>."), "cards": [c("Condivisione e upload", "Controllo upload per banda larga", "Target limitati per slot, riciclo degli slot deboli, lettura dei ratio e controlli di seeding mantengono utili gli upload veloci senza cambiare il protocollo eD2K."), c("Controllo rete", "Binding, NAT e policy di esposizione", "Interface-aware binding, validazione UPnP/NAT, HTTPS, regole allowed-IP ed ereditarietà WebServer mantengono esplicite e testabili le superfici remote."), c("Prestazione e scala", "Default attuali per sessioni grandi", "Buffer socket maggiori, limiti queue/source, file buffering, timeout, sync ricorsiva e guida long paths puntano a Windows attuali e grandi librerie."), c("Rete classica", "eD2K e Kad restano al centro", "Ricerca Server, globale e Kad restano la base nativa, con identità Kad, gestione nodi cattivi, cleanup e timing entro confini compatibili."), c("Automazione", "REST e workflow di controllo", "Endpoint JSON autenticati coprono trasferimenti, ricerche, file condivisi, server, Kad, log, categorie, upload, statistiche, preferenze e shutdown controllato."), c("Disciplina di release", "Evidenza prima dei pacchetti pubblici", "La beta <code>0.7.3</code> dipende da test nativi, contratti REST, lane live dei controller, avversità di rete, packaging e prove x64/ARM64.")]},
                "guide": {**s("Guida prodotto", "Un modello operativo breve"), "cards": [c("", "Parti dalle buone abitudini di eMule", "Usa liste server fidate, avvia Kad con attenzione, mantieni prevedibili incoming e cartelle condivise e conserva il workflow classico prima dell'automazione."), c("", "Regola l'upload sul link reale", "Imposta un limite finito, scegli un target realistico di client e lascia che la policy banda larga favorisca meno slot ma più solidi."), c("", "Cura le grandi librerie", "Usa Windows con long paths, tieni pulite le radici condivise, osserva i ratio e tratta i file rari come scelte deliberate di pubblicazione."), c("", "Automatizza solo su reti fidate", "Abilita WebServer/REST con API key, applica binding e firewall con cura e usa controller che rispettino la semantica nativa di eMule."), c("", "Segui la prontezza della release", "Considera la branch pubblica come pre-release attivo finché i gate <code>0.7.3</code>, i check operatore e l'evidenza live E2E non dicono altro."), c("", "Usa la documentazione per i dettagli", "La homepage resta compatta. Guida prodotto, contratto REST, note banda larga e documenti release sono Markdown nel repository di tooling.")]},
                "automation": {"eyebrow": "Superficie di controllo", "h2": "REST automation senza sostituire l'app desktop", "p": "La linea di release banda larga espone una JSON API <code>/api/v1</code> orientata alle risorse dal listener WebServer esistente. Autentica con <code>X-API-Key</code>, serve envelope JSON e mantiene le modifiche allo stato eMule instradate tramite l'app.", "pills_label": "Aree REST API", "pills": ["Trasferimenti", "Ricerche", "Server", "Kad", "File condivisi", "Upload", "Categorie", "Log", "Statistiche", "Preferenze"]},
                "release": {**s("Stato della release", "La release pubblica 0.7.3 è pianificata, ha gate e non è ancora uscita"), "cards": [c("", "Stato attuale", "Il primo target pubblico è <code>0.7.3</code>. Non è ancora uscito. La prova finale è in pausa su indicazione dell'operatore e lo stato pubblico resta legato ai documenti attivi."), c("", "Prova di build e pacchetto", "La prova richiesta copre validazione workspace, build Debug e Release x64, build Release ARM64, binari di test, generazione pacchetti, worktree pulita e hash SHA-256."), c("", "Prova di comportamento", "I gate coprono suite native, contratto REST, drift OpenAPI, request malformate, automazione UI, E2E live dei controller, Release x64 live E2E completo e avversità di rete."), c("", "Prova dei controller", "aMuTorrent, Prowlarr, Radarr, Sonarr e lane compatibili qBittorrent provano automazione senza indebolire il contratto nativo <code>/api/v1</code>."), c("", "Prova di compatibilità", "Il comportamento eD2K/Kad originale resta default. Banda larga, REST e controller vengono aggiunti attorno a questo obiettivo di compatibilità.")]},
                "method": {**s("Metodo di implementazione", "Modernizzare intorno al nucleo legacy, poi provare il risultato", "Lo stile è intenzionalmente conservativo. eMule BB cambia policy locali, limiti, diagnostica, confini API e disciplina di release mantenendo default la compatibilità eD2K/Kad."), "cards": [c("Compatibilità", "Niente drift casuale del protocollo", "Le modifiche Kad ed eD2K restano in routing locale, timing, validazione e controllo. Wire format, opcode e workflow desktop nativi sono confini di compatibilità."), c("Limiti", "Default fissi e revisionabili", "Ipotesi moderne su bandwidth, memoria, socket, queue e timeout sono default espliciti o preferenze avanzate, non comportamento adattivo nascosto."), c("REST", "Contratti di controllo, non screen scraping", "La JSON API autenticata segue un contratto OpenAPI, respinge input malformati e instrada le mutazioni native tramite l'app."), c("Release", "Evidenza prima delle etichette", "Il processo registra comandi, commit, log, percorsi pacchetto, hash, evidenza live e decisioni operatore così il tag è un esito verificato.")]},
                "repos": {**s("Workspace pubblico", "Repository principali"), "links": []},
                "team": {**s("Cultura del progetto", "Le persone che impediscono alla queue di diventare teatro prestazionale"), "cards": [c("", "Terapeuta degli upload slot", "Aiuta gli slot deboli a elaborare i propri sentimenti il tempo giusto prima di rimandarli in queue con appunti e cooldown."), c("", "Archivista del bootstrap Kad", "Custodisce la lista sacra di nodi che funzionò una volta nel 2007 e merita una seconda occasione ben validata."), c("", "Addetto ai gate di release", "Fa entrare le build solo se portano test, evidenza live e una spiegazione plausibile sull'ultimo socket.")]},
            },
        ),
        "de": clone_base(
            "de",
            {
                "title": "eMule broadband edition | eMule BB auf Deutsch",
                "meta_description": "eMule BB ist eine moderne eMule-Ausgabe für Breitband-Upload-Kontrolle, VPN/interface binding, aktuelle Leistungsgrenzen, große Freigaben, REST automation, eD2K, Kad und Power-User-Workflows.",
                "og_title": "eMule broadband edition | eMule BB auf Deutsch",
                "og_description": "Moderner eMule für Breitband-Upload-Kontrolle, VPN/interface binding, aktuelle Leistungsgrenzen, große Bibliotheken, REST automation, eD2K/Kad-Kompatibilität und Release-Validierung. Die erste öffentliche Version 0.7.3 ist geplant und noch nicht veröffentlicht.",
                "structured_description": "Moderner eMule für Breitband-Upload-Kontrolle, VPN/interface binding, aktuelle Leistungsgrenzen, große Freigaben, REST automation, eD2K/Kad-Kompatibilität und Power-User-Workflows. Die erste öffentliche Version ist als 0.7.3 geplant und noch nicht veröffentlicht.",
                "nav_label": "Hauptnavigation",
                "project_links_label": "Projektlinks",
                "product_summary_label": "eMule BB Kurzfassung",
                "footer_links_label": "Footer-Links",
                "nav": [{"id": "why", "label": "Warum"}, {"id": "features", "label": "Funktionen"}, {"id": "guide", "label": "Guide"}, {"id": "docs", "label": "Dokumentation"}, {"id": "automation", "label": "Automatisierung"}, {"id": "release", "label": "Veröffentlichung"}, {"id": "repos", "label": "Repos"}],
                "hero": {"eyebrow": "Klassischer eMule, abgestimmt auf heutige Breitbandanschlüsse", "h1": "eMule BB hält eD2K und Kad für ernsthafte Nutzer brauchbar.", "lead": "Ein eMule für Power User mit schnellen Uploads, großen Freigaben, dauerhaft laufenden Windows-Sitzungen und lokalen Controller-Workflows, ohne die vertraute Desktop-App aufzugeben.", "source": "Quellcode", "guide": "Produktguide", "panel_kicker": "Produktlinie", "panel_h2": "Konservativ, wo Kompatibilität zählt. Modern, wo Kontrolle zählt.", "panel_p": "eMule BB stellt den nativen eMule-Workflow in den Mittelpunkt und ergänzt ihn um breitbandtaugliche Queue-Logik, lokale API-Steuerung und Release-Validierung.", "signals": ["Originale eD2K/Kad-Kompatibilität", "Kontrolle der Upload-Slots", "VPN/interface binding", "Aktuelle Leistungsgrenzen", "Authentifizierte JSON REST API", "Öffentliche 0.7.3 geplant", "Workspace für Release-Validierung"]},
                "intro": "eMule broadband edition, kurz <strong>eMule BB</strong>, ist eine eigenständige Produktlinie für Menschen, die das verteilte Modell von eMule weiterhin schätzen. Sie bewahrt die klassischen Desktop-Workflows und macht den Client auf heutigen Windows-Systemen leichter betreibbar, beobachtbar, automatisierbar und validierbar.",
                "why": {**s("Warum", "Ein Legacy-Client ist nur nützlich, wenn man ihn noch verlässlich betreiben kann", "eMule BB ist Produktarbeit und disziplinierte Technik zugleich: eine native Windows-Anwendung mit echtem Netzwerkverhalten erhalten und mit modernem Build-, Test-, Dokumentations-, Automatisierungs- und Release-Prozess umgeben."), "cards": [c("Produktgrund", "eD2K und Kad praktisch halten", "Es geht nicht um Nostalgie und nicht um einen Rewrite. Das klassische Modell soll für lange Sitzungen, seltene Dateien, bewusstes Seeding und native Desktop-Nutzung brauchbar bleiben."), c("Technischer Grund", "Alte Annahmen sichtbar machen", "Defaults für Upload-Slots, Timeouts, Buffer, große Freigaben und WebServer-Exposition werden explizit, damit sie geprüft, getestet und dokumentiert werden können."), c("Release-Grund", "Moderne Nachweise auf Legacy-Code anwenden", "Der Workspace behandelt Release als technisches Artefakt: Source-Policy, OpenAPI-Verträge, reproduzierbare Builds, Hashes, Live-Prüfungen und Operator-Gates müssen zusammenpassen.")]},
                "features": {**s("Funktionen", "Was eMule BB um den klassischen Client ergänzt", "Die Arbeit zielt auf sichtbares Betreiberverhalten: vorhersehbare Upload-Policy, sichereres binding, feste Leistungsgrenzen, große Freigaben, lokale Automatisierung und Nachweise für das geplante Release <code>0.7.3</code>."), "cards": [c("Freigabe und Upload", "Breitband-Upload-Kontrolle", "Begrenzte Slot-Ziele, Recycling schwacher Slots, Ratio-Anzeigen und Seeding-Kontrollen halten schnelle Uploads nützlich, ohne das eD2K-Upload-Protokoll zu ändern."), c("Netzwerkkontrolle", "Binding, NAT und Expositions-Policy", "Interface-aware binding, UPnP/NAT-Validierung, HTTPS, allowed-IP-Regeln und WebServer-Vererbung halten entfernte Oberflächen explizit und testbar."), c("Leistung und Skalierung", "Aktuelle Defaults für große Sitzungen", "Größere Socket-Buffer, Queue/Source-Limits, file buffering, Timeouts, rekursive Sync und long-path guidance zielen auf heutige Windows-Systeme und große Freigaben."), c("Klassisches Netzwerk", "eD2K und Kad bleiben zuerst", "Server-, globale und Kad-Suche bleiben die native Basis, mit Kad-Identität, Bad-Node-Behandlung, Cleanup und Timing innerhalb kompatibler Grenzen."), c("Automatisierung", "REST und Controller-Workflows", "Authentifizierte JSON-Endpunkte decken Transfers, Suchen, Freigaben, Server, Kad, Logs, Kategorien, Uploads, Statistiken, Preferences und kontrolliertes Shutdown ab."), c("Release-Disziplin", "Nachweise vor öffentlichen Paketen", "Die geplante Beta <code>0.7.3</code> hängt von nativen Tests, REST-Verträgen, Live-Controller-Lanes, Netzwerk-Adversity, Packaging und x64/ARM64-Proben ab.")]},
                "guide": {**s("Produktguide", "Ein kurzes Betriebsmodell"), "cards": [c("", "Mit bewährten eMule-Gewohnheiten starten", "Nutze vertrauenswürdige Serverlisten, starte Kad bewusst, halte incoming und freigegebene Ordner berechenbar und bewahre den klassischen Workflow vor der Automatisierung."), c("", "Upload auf den echten Anschluss abstimmen", "Setze ein endliches Upload-Limit, wähle ein realistisches Client-Ziel und lass die Breitband-Policy weniger, aber stärkere Slots bevorzugen."), c("", "Große Freigaben pflegen", "Nutze Windows mit long paths, halte Freigabe-Wurzeln sauber, beobachte Ratios und behandle seltene Dateien als bewusste Veröffentlichungen."), c("", "Nur in vertrauenswürdigen Netzen automatisieren", "Aktiviere WebServer/REST mit API key, setze binding und Firewall sauber und nutze Controller, die native eMule-Semantik respektieren."), c("", "Release-Reife verfolgen", "Betrachte die öffentliche Branch als aktives Pre-Release, bis <code>0.7.3</code>-Gates, Operator-Checks und Live-E2E-Nachweise etwas anderes sagen."), c("", "Für Tiefe die Dokumentation nutzen", "Die Homepage bleibt kompakt. Produktguide, REST-Vertrag, Breitbandnotizen und Release-Dokumente liegen als Markdown im Tooling-Repository.")]},
                "automation": {"eyebrow": "Controller-Oberfläche", "h2": "REST automation, ohne die Desktop-App zu ersetzen", "p": "Die Breitband-Release-Linie stellt über den vorhandenen WebServer-Listener eine ressourcenorientierte JSON API <code>/api/v1</code> bereit. Sie authentifiziert mit <code>X-API-Key</code>, liefert JSON-Envelopes und führt native eMule-Statusänderungen über die App.", "pills_label": "REST API Bereiche", "pills": ["Transfers", "Suchen", "Server", "Kad", "Freigaben", "Uploads", "Kategorien", "Logs", "Statistiken", "Preferences"]},
                "release": {**s("Release-Status", "Die öffentliche Version 0.7.3 ist geplant, gegated und noch nicht veröffentlicht"), "cards": [c("", "Aktueller Stand", "Das erste öffentliche Ziel ist <code>0.7.3</code>. Es ist noch nicht veröffentlicht. Der finale Nachweis ist durch Operator-Vorgabe pausiert, der öffentliche Stand bleibt an aktive Release-Dokumente gebunden."), c("", "Build- und Paketnachweis", "Der Nachweis umfasst Workspace-Validierung, Debug- und Release-x64-Builds, Release-ARM64-Builds, Test-Binaries, Paketgenerierung, saubere Worktree und SHA-256-Hashes."), c("", "Verhaltensnachweis", "Die Gates umfassen native Suites, REST-Vertrag, OpenAPI drift, malformed requests, UI automation, live Controller-Surface E2E, vollständiges Release x64 live E2E und Netzwerk-Adversity."), c("", "Controller-Nachweis", "aMuTorrent, Prowlarr, Radarr, Sonarr und qBittorrent-kompatible Lanes zeigen Automatisierung, ohne den nativen Vertrag <code>/api/v1</code> zu schwächen."), c("", "Kompatibilitätsnachweis", "Das originale eD2K/Kad-Verhalten bleibt Default. Breitband, REST und Controller werden um dieses Kompatibilitätsziel herum ergänzt.")]},
                "method": {**s("Implementierungsmethode", "Um den Legacy-Kern modernisieren, dann das Ergebnis beweisen", "Der Stil ist bewusst konservativ. eMule BB ändert lokale Policy, Limits, Diagnostik, API-Grenzen und Release-Disziplin, während eD2K/Kad-Kompatibilität Default bleibt."), "cards": [c("Kompatibilität", "Kein beiläufiger Protocol drift", "Kad- und eD2K-Änderungen bleiben in lokalem Routing, Timing, Validierung und Kontrolle. Wire formats, opcodes und native Workflows sind Kompatibilitätsgrenzen."), c("Limits", "Feste, prüfbare Defaults", "Moderne Annahmen zu bandwidth, Speicher, socket, queue und timeout werden als explizite Defaults oder Advanced Preferences abgebildet."), c("REST", "Controller-Verträge, kein screen scraping", "Die authentifizierte JSON API folgt einem OpenAPI-Vertrag, lehnt malformed inputs ab und führt native Mutationen über die App."), c("Release", "Nachweise vor Labels", "Der Prozess zeichnet Befehle, Commits, Logs, Paketpfade, Hashes, Live-Nachweise und Operator-Entscheidungen auf, damit ein Tag ein geprüftes Ergebnis ist.")]},
                "repos": {**s("Öffentlicher Workspace", "Primäre Repositories"), "links": []},
                "team": {**s("Projektkultur", "Die Leute, die verhindern, dass die Queue zur Performance-Kunst wird"), "cards": [c("", "Upload-Slot-Therapeut", "Gibt schwachen Slots genau lange genug Raum für ihre Gefühle, bevor sie mit Formular und cooldown zurück in die Queue gehen."), c("", "Kad-Bootstrap-Archivar", "Bewahrt die heilige Liste von Nodes, die 2007 einmal funktionierten und eine sorgfältig validierte zweite Chance verdienen."), c("", "Release-Gate-Türsteher", "Lässt Builds nur herein, wenn sie Tests, Live-Nachweise und eine plausible Erklärung zum letzten Socket mitbringen.")]},
            },
        ),
        "fr": clone_base(
            "fr",
            {
                "title": "eMule broadband edition | eMule BB en français",
                "meta_description": "eMule BB est une édition moderne d'eMule pour le contrôle d'upload haut débit, VPN/interface binding, des limites de performance actuelles, de grandes bibliothèques partagées, REST automation, eD2K, Kad et des workflows avancés.",
                "og_title": "eMule broadband edition | eMule BB en français",
                "og_description": "eMule moderne pour le contrôle d'upload haut débit, VPN/interface binding, de grandes bibliothèques, REST automation, la compatibilité eD2K/Kad et la validation de release. La première version publique 0.7.3 est prévue et n'est pas encore publiée.",
                "structured_description": "eMule moderne pour le contrôle d'upload haut débit, VPN/interface binding, de grandes bibliothèques partagées, REST automation, la compatibilité eD2K/Kad et des workflows avancés. La première version publique est prévue comme 0.7.3 et n'est pas encore publiée.",
                "nav_label": "Navigation principale",
                "project_links_label": "Liens du projet",
                "product_summary_label": "Résumé eMule BB",
                "footer_links_label": "Liens de pied de page",
                "nav": [{"id": "why", "label": "Pourquoi"}, {"id": "features", "label": "Fonctions"}, {"id": "guide", "label": "Guide"}, {"id": "docs", "label": "Documentation"}, {"id": "automation", "label": "Automatisation"}, {"id": "release", "label": "Publication"}, {"id": "repos", "label": "Dépôts"}],
                "hero": {"eyebrow": "L'eMule classique, réglé pour le haut débit actuel", "h1": "eMule BB garde eD2K et Kad utiles pour les utilisateurs exigeants.", "lead": "Un eMule pour utilisateurs avancés, avec uploads rapides, grandes bibliothèques partagées, sessions Windows permanentes et workflows locaux de contrôle sans abandonner l'application desktop familière.", "source": "Code source", "guide": "Guide produit", "panel_kicker": "Positionnement", "panel_h2": "Conservateur quand la compatibilité compte. Moderne quand le contrôle compte.", "panel_p": "eMule BB garde le workflow natif d'eMule au centre et ajoute une gestion de queue adaptée au haut débit, un contrôle local par API et une validation de release.", "signals": ["Compatibilité eD2K/Kad d'origine", "Contrôle des upload slots", "VPN/interface binding", "Limites de performance actuelles", "JSON REST API authentifiée", "0.7.3 publique prévue", "Workspace de validation release"]},
                "intro": "eMule broadband edition, ou simplement <strong>eMule BB</strong>, est une ligne de produit indépendante pour celles et ceux qui accordent encore de la valeur au modèle distribué d'eMule. Elle conserve les workflows desktop classiques et rend le client plus simple à exécuter, observer, automatiser et valider sur les systèmes Windows actuels.",
                "why": {**s("Pourquoi", "Un client legacy n'est utile que s'il reste exploitable avec confiance", "eMule BB est à la fois un produit et une discipline d'ingénierie : préserver une application Windows native avec un vrai comportement réseau, puis l'entourer de build, tests, documentation, automatisation et processus de release modernes."), "cards": [c("Raison produit", "Garder eD2K et Kad pratiques", "Le but n'est ni la nostalgie ni une réécriture. Il s'agit de garder le modèle classique utilisable pour les longues sessions, les fichiers rares, le seeding volontaire et les utilisateurs qui veulent encore un client natif."), c("Raison technique", "Rendre visibles les anciennes hypothèses", "Les defaults d'upload slots, timeouts, buffers, grandes bibliothèques et exposition WebServer deviennent explicites, donc révisables, testables et documentables."), c("Raison release", "Appliquer une preuve moderne à du code legacy", "Le workspace traite la release comme un artefact d'ingénierie : politique source, contrats OpenAPI, builds reproductibles, hashes, contrôles live et gates opérateur doivent converger.")]},
                "features": {**s("Fonctions", "Ce qu'eMule BB ajoute autour du client classique", "Le travail vise le comportement visible par l'opérateur : upload prévisible, binding plus sûr, limites fixes de performance, grandes bibliothèques, automatisation locale et preuves pour la release prévue <code>0.7.3</code>."), "cards": [c("Partage et upload", "Contrôle d'upload haut débit", "Objectifs de slots bornés, recyclage des slots faibles, lecture des ratios et contrôles de seeding gardent les liens rapides utiles sans changer le protocole eD2K."), c("Contrôle réseau", "Binding, NAT et exposition", "Interface-aware binding, validation UPnP/NAT, HTTPS, règles allowed-IP et héritage WebServer gardent les surfaces distantes explicites et testables."), c("Performance et échelle", "Defaults actuels pour grandes sessions", "Buffers socket plus élevés, limites queue/source, file buffering, timeouts, sync récursive et long paths ciblent Windows actuels et les grandes bibliothèques."), c("Réseau classique", "eD2K et Kad restent prioritaires", "Les recherches Server, globales et Kad restent la base native, avec identité Kad, traitement des mauvais nœuds, cleanup et timing dans des limites compatibles."), c("Automatisation", "REST et workflows de contrôle", "Des endpoints JSON authentifiés couvrent transferts, recherches, fichiers partagés, serveurs, Kad, logs, catégories, uploads, statistiques, préférences et shutdown contrôlé."), c("Discipline de release", "Des preuves avant les paquets publics", "La beta <code>0.7.3</code> dépend de tests natifs, contrats REST, lanes live de contrôleurs, adversité réseau, packaging et répétitions x64/ARM64.")]},
                "guide": {**s("Guide produit", "Un modèle court d'exploitation"), "cards": [c("", "Partir des bonnes habitudes eMule", "Utilisez des listes de serveurs fiables, amorcez Kad avec attention, gardez incoming et dossiers partagés prévisibles et conservez le workflow classique avant l'automatisation."), c("", "Régler l'upload sur le lien réel", "Définissez une limite d'upload finie, choisissez une cible réaliste de clients et laissez la politique haut débit favoriser moins de slots, mais plus solides."), c("", "Soigner les grandes bibliothèques", "Utilisez Windows avec long paths, gardez les racines de partage propres, suivez les ratios et traitez les fichiers rares comme des choix de publication."), c("", "Automatiser seulement sur des réseaux fiables", "Activez WebServer/REST avec API key, appliquez binding et firewall soigneusement et utilisez des contrôleurs respectant la sémantique native d'eMule."), c("", "Suivre la préparation de la release", "Considérez la branche publique comme pre-release actif jusqu'à ce que les gates <code>0.7.3</code>, contrôles opérateur et preuves live E2E disent le contraire."), c("", "Utiliser la documentation pour le détail", "La page d'accueil reste compacte. Guide produit, contrat REST, notes haut débit et documents de release vivent en Markdown dans le dépôt tooling.")]},
                "automation": {"eyebrow": "Surface de contrôle", "h2": "REST automation sans remplacer l'application desktop", "p": "La ligne de release haut débit expose une JSON API <code>/api/v1</code> orientée ressources depuis le listener WebServer existant. Elle authentifie avec <code>X-API-Key</code>, sert des enveloppes JSON et garde les changements d'état eMule relayés par l'application.", "pills_label": "Domaines REST API", "pills": ["Transferts", "Recherches", "Serveurs", "Kad", "Fichiers partagés", "Uploads", "Catégories", "Logs", "Statistiques", "Préférences"]},
                "release": {**s("État de release", "La version publique 0.7.3 est prévue, soumise à gates et pas encore publiée"), "cards": [c("", "État actuel", "La première cible publique est <code>0.7.3</code>. Elle n'est pas encore publiée. La preuve finale est suspendue par consigne opérateur et l'état public reste lié aux documents actifs."), c("", "Preuve de build et paquet", "La preuve requise couvre validation workspace, builds Debug et Release x64, builds Release ARM64, binaires de test, génération de paquet, worktree propre et hashes SHA-256."), c("", "Preuve de comportement", "Les gates couvrent suites natives, contrat REST, drift OpenAPI, requests malformées, UI automation, E2E live des contrôleurs, Release x64 live E2E complet et adversité réseau."), c("", "Preuve des contrôleurs", "aMuTorrent, Prowlarr, Radarr, Sonarr et lanes compatibles qBittorrent prouvent l'automatisation sans affaiblir le contrat natif <code>/api/v1</code>."), c("", "Preuve de compatibilité", "Le comportement eD2K/Kad d'origine reste default. Haut débit, REST et contrôleurs s'ajoutent autour de cet objectif de compatibilité.")]},
                "method": {**s("Méthode d'implémentation", "Moderniser autour du noyau legacy, puis prouver le résultat", "Le style est volontairement conservateur. eMule BB modifie politique locale, limites, diagnostics, frontières API et discipline de release tout en gardant la compatibilité eD2K/Kad par défaut."), "cards": [c("Compatibilité", "Pas de protocol drift au hasard", "Les changements Kad et eD2K restent dans le routage local, le timing, la validation et le contrôle. Wire formats, opcodes et workflows natifs restent des frontières."), c("Limites", "Defaults fixes et révisables", "Les hypothèses modernes de bandwidth, mémoire, socket, queue et timeout sont exprimées comme defaults explicites ou préférences avancées."), c("REST", "Contrats de contrôle, pas de screen scraping", "La JSON API authentifiée suit un contrat OpenAPI, rejette les entrées malformées et relaie les mutations natives par l'application."), c("Release", "Des preuves avant les labels", "Le processus enregistre commandes, commits, logs, chemins de paquets, hashes, preuves live et décisions opérateur pour qu'un tag soit un résultat vérifié.")]},
                "repos": {**s("Workspace public", "Dépôts principaux"), "links": []},
                "team": {**s("Culture du projet", "L'équipe qui empêche la queue de devenir du théâtre de performance"), "cards": [c("", "Thérapeute des upload slots", "Laisse les slots faibles gérer leurs émotions juste assez longtemps avant de les renvoyer dans la queue avec formulaire et cooldown."), c("", "Archiviste du bootstrap Kad", "Garde la liste sacrée de nœuds qui a fonctionné une fois en 2007 et mérite une seconde chance soigneusement validée."), c("", "Videur des gates de release", "Ne laisse entrer les builds que s'ils apportent tests, preuves live et explication crédible du dernier socket.")]},
            },
        ),
        "ru": clone_base(
            "ru",
            {
                "title": "eMule broadband edition | eMule BB на русском",
                "meta_description": "eMule BB — современная редакция eMule для контроля upload на широкополосных линиях, VPN/interface binding, актуальных лимитов производительности, больших shared libraries, REST automation, eD2K, Kad и продвинутых workflows.",
                "og_title": "eMule broadband edition | eMule BB на русском",
                "og_description": "Современный eMule для контроля upload, VPN/interface binding, больших библиотек, REST automation, совместимости eD2K/Kad и release-валидации. Первая публичная версия 0.7.3 запланирована и еще не выпущена.",
                "structured_description": "Современный eMule для контроля upload на широкополосных линиях, VPN/interface binding, больших shared libraries, REST automation, совместимости eD2K/Kad и продвинутых workflows. Первая публичная версия запланирована как 0.7.3 и еще не выпущена.",
                "nav_label": "Основная навигация",
                "project_links_label": "Ссылки проекта",
                "product_summary_label": "Кратко об eMule BB",
                "footer_links_label": "Ссылки внизу страницы",
                "nav": [{"id": "why", "label": "Зачем"}, {"id": "features", "label": "Возможности"}, {"id": "guide", "label": "Гайд"}, {"id": "docs", "label": "Документация"}, {"id": "automation", "label": "Автоматизация"}, {"id": "release", "label": "Выпуск"}, {"id": "repos", "label": "Репозитории"}],
                "hero": {"eyebrow": "Классический eMule, настроенный для современного широкополосного доступа", "h1": "eMule BB сохраняет eD2K и Kad полезными для требовательных пользователей.", "lead": "eMule для опытных пользователей: быстрый upload, большие shared libraries, постоянные сессии Windows и локальные controller workflows без отказа от привычного desktop-приложения.", "source": "Исходный код", "guide": "Гайд по продукту", "panel_kicker": "Позиция продукта", "panel_h2": "Консервативен там, где важна совместимость. Современен там, где важен контроль.", "panel_p": "eMule BB оставляет нативный workflow eMule в центре и добавляет очереди для широкополосного upload, локальное управление через API и release-валидацию.", "signals": ["Оригинальная совместимость eD2K/Kad", "Контроль upload slots", "VPN/interface binding", "Актуальные лимиты производительности", "Аутентифицированная JSON REST API", "Публичная 0.7.3 запланирована", "Workspace для release-валидации"]},
                "intro": "eMule broadband edition, коротко <strong>eMule BB</strong>, — независимая продуктовая линия для тех, кому по-прежнему важна распределенная модель eMule. Она сохраняет классические desktop workflows и делает клиент проще в запуске, наблюдении, автоматизации и проверке на современных Windows-системах.",
                "why": {**s("Зачем", "Legacy-клиент полезен только тогда, когда им все еще можно уверенно управлять", "eMule BB — это продуктовая работа и инженерная дисциплина: сохранить нативное Windows-приложение с реальным сетевым поведением и окружить его современными build, тестами, документацией, автоматизацией и release-процессом."), "cards": [c("Причина продукта", "Сохранить eD2K и Kad практичными", "Цель — не ностальгия и не rewrite. Важно сохранить классическую модель для длинных сессий, редких файлов, осознанного seeding и нативного клиента."), c("Техническая причина", "Вывести старые предположения на свет", "Defaults для upload slots, timeouts, buffers, больших библиотек и WebServer становятся явными, чтобы их можно было проверять и документировать."), c("Причина release", "Доказывать legacy-код современным способом", "Workspace относится к release как к инженерному артефакту: source policy, OpenAPI-контракты, воспроизводимые builds, hashes, live checks и operator gates должны сходиться.")]},
                "features": {**s("Возможности", "Что eMule BB добавляет вокруг классического клиента", "Работа сосредоточена на поведении, видимом оператору: предсказуемый upload, более безопасный binding, фиксированные лимиты, большие библиотеки, локальная автоматизация и доказательства для запланированного release <code>0.7.3</code>."), "cards": [c("Обмен и upload", "Контроль upload на широкополосных линиях", "Ограниченные цели slots, переработка слабых slots, ratio-индикаторы и seeding controls сохраняют быстрый upload полезным без изменения протокола eD2K."), c("Контроль сети", "Binding, NAT и политика экспозиции", "Interface-aware binding, проверка UPnP/NAT, HTTPS, allowed-IP rules и наследование WebServer делают удаленные поверхности явными и тестируемыми."), c("Производительность и масштаб", "Актуальные defaults для больших сессий", "Большие socket buffers, queue/source limits, file buffering, timeouts, рекурсивная sync и long paths ориентированы на современные Windows и большие библиотеки."), c("Классическая сеть", "eD2K и Kad остаются первыми", "Server, global и Kad search остаются нативной основой; Kad identity, bad-node handling, cleanup и timing остаются в границах совместимости."), c("Автоматизация", "REST и controller workflows", "Аутентифицированные JSON endpoints покрывают transfers, searches, shared files, servers, Kad, logs, categories, uploads, statistics, preferences и controlled shutdown."), c("Дисциплина release", "Доказательства до публичных пакетов", "Бета <code>0.7.3</code> зависит от native tests, REST contracts, live controller lanes, network adversity, packaging и репетиций x64/ARM64.")]},
                "guide": {**s("Гайд по продукту", "Короткая модель эксплуатации"), "cards": [c("", "Начинайте с проверенных привычек eMule", "Используйте надежные server lists, осознанно запускайте Kad, держите incoming и shared folders предсказуемыми и сохраняйте классический workflow до автоматизации."), c("", "Настройте upload под реальный канал", "Задайте конечный upload limit, выберите реалистичную цель клиентов и позвольте broadband policy предпочитать меньше, но сильнее slots."), c("", "Ухаживайте за большими библиотеками", "Используйте Windows с long paths, держите shared roots чистыми, следите за ratios и относитесь к редким файлам как к осознанной публикации."), c("", "Автоматизируйте только в доверенных сетях", "Включайте WebServer/REST с API key, аккуратно настраивайте binding и firewall и используйте controllers, уважающие нативную семантику eMule."), c("", "Следите за готовностью release", "Считайте публичную branch активным pre-release, пока gates <code>0.7.3</code>, operator checks и live E2E evidence не покажут обратное."), c("", "За деталями идите в документацию", "Homepage остается компактной. Гайд по продукту, REST contract, заметки о broadband и release docs живут как Markdown в tooling repository.")]},
                "automation": {"eyebrow": "Поверхность управления", "h2": "REST automation без замены desktop-приложения", "p": "Broadband release track открывает resource-oriented JSON API <code>/api/v1</code> через существующий WebServer listener. Она использует <code>X-API-Key</code>, отдает JSON envelopes и проводит изменения состояния eMule через приложение.", "pills_label": "Области REST API", "pills": ["Transfers", "Searches", "Servers", "Kad", "Shared files", "Uploads", "Categories", "Logs", "Statistics", "Preferences"]},
                "release": {**s("Состояние release", "Публичная версия 0.7.3 запланирована, проходит gates и еще не выпущена"), "cards": [c("", "Текущий статус", "Первый публичный target — <code>0.7.3</code>. Он еще не выпущен. Финальное доказательство приостановлено по указанию оператора, а публичный статус связан с активными release docs."), c("", "Доказательство build и пакета", "Доказательство покрывает workspace validation, Debug и Release x64 app builds, Release ARM64 app builds, test binaries, package generation, clean worktree и SHA-256 hashes."), c("", "Доказательство поведения", "Gates покрывают native suites, REST contract, OpenAPI drift, malformed requests, UI automation, live controller-surface E2E, полный Release x64 live E2E и network adversity."), c("", "Доказательство controllers", "aMuTorrent, Prowlarr, Radarr, Sonarr и qBittorrent-compatible lanes показывают automation без ослабления нативного контракта <code>/api/v1</code>."), c("", "Доказательство совместимости", "Оригинальное поведение eD2K/Kad остается default. Broadband, REST и controllers добавляются вокруг этой цели совместимости.")]},
                "method": {**s("Метод реализации", "Модернизировать вокруг legacy-ядра, затем доказать результат", "Стиль намеренно консервативен. eMule BB меняет локальную policy, limits, diagnostics, API boundaries и release discipline, сохраняя совместимость eD2K/Kad по умолчанию."), "cards": [c("Совместимость", "Без случайного protocol drift", "Изменения Kad и eD2K остаются в локальных routing, timing, validation и control paths. Wire formats, opcodes и native desktop workflows — границы совместимости."), c("Лимиты", "Фиксированные и проверяемые defaults", "Современные предположения о bandwidth, memory, socket, queue и timeout выражены как явные defaults или advanced preferences."), c("REST", "Controller contracts, не screen scraping", "Аутентифицированная JSON API следует OpenAPI-backed contract, отклоняет malformed inputs и проводит native state mutations через приложение."), c("Release", "Доказательства перед labels", "Процесс записывает commands, commits, logs, package paths, hashes, live evidence и operator decisions, чтобы tag был проверенным результатом.")]},
                "repos": {**s("Публичный workspace", "Основные репозитории"), "links": []},
                "team": {**s("Культура проекта", "Люди, которые не дают queue стать перформансом"), "cards": [c("", "Терапевт upload slots", "Дает слабым slots ровно столько времени на переживания, сколько нужно, а затем возвращает их в queue с формой и cooldown."), c("", "Архивариус bootstrap Kad", "Хранит священный список nodes, который однажды работал в 2007 году и заслуживает аккуратно проверенного второго шанса."), c("", "Охранник release gates", "Пропускает builds только с тестами, live evidence и убедительным объяснением судьбы последнего socket.")]},
            },
        ),
        "pl": clone_base(
            "pl",
            {
                "title": "eMule broadband edition | eMule BB po polsku",
                "meta_description": "eMule BB to nowoczesna edycja eMule do kontroli uploadu na szybkich łączach, VPN/interface binding, aktualnych limitów wydajności, dużych bibliotek współdzielonych, REST automation, eD2K, Kad i zaawansowanych workflows.",
                "og_title": "eMule broadband edition | eMule BB po polsku",
                "og_description": "Nowoczesny eMule do kontroli uploadu, VPN/interface binding, dużych bibliotek, REST automation, zgodności eD2K/Kad i walidacji release. Pierwsza publiczna wersja 0.7.3 jest planowana i nie została jeszcze wydana.",
                "structured_description": "Nowoczesny eMule do kontroli uploadu na szybkich łączach, VPN/interface binding, dużych bibliotek współdzielonych, REST automation, zgodności eD2K/Kad i zaawansowanych workflows. Pierwsza publiczna wersja jest planowana jako 0.7.3 i nie została jeszcze wydana.",
                "nav_label": "Główna nawigacja",
                "project_links_label": "Linki projektu",
                "product_summary_label": "Podsumowanie eMule BB",
                "footer_links_label": "Linki w stopce",
                "nav": [{"id": "why", "label": "Dlaczego"}, {"id": "features", "label": "Funkcje"}, {"id": "guide", "label": "Przewodnik"}, {"id": "docs", "label": "Dokumentacja"}, {"id": "automation", "label": "Automatyzacja"}, {"id": "release", "label": "Wydanie"}, {"id": "repos", "label": "Repozytoria"}],
                "hero": {"eyebrow": "Klasyczny eMule, dostrojony do współczesnych łączy", "h1": "eMule BB utrzymuje eD2K i Kad jako użyteczne narzędzia dla wymagających użytkowników.", "lead": "eMule dla power userów: szybki upload, duże biblioteki współdzielone, stale działające sesje Windows i lokalne controller workflows bez porzucania znanej aplikacji desktop.", "source": "Kod źródłowy", "guide": "Przewodnik produktu", "panel_kicker": "Podejście produktu", "panel_h2": "Konserwatywnie tam, gdzie liczy się zgodność. Nowocześnie tam, gdzie liczy się kontrola.", "panel_p": "eMule BB zostawia natywny workflow eMule w centrum i dodaje obsługę queue dla szybkich łączy, lokalne sterowanie przez API oraz walidację release.", "signals": ["Oryginalna zgodność eD2K/Kad", "Kontrola upload slots", "VPN/interface binding", "Aktualne limity wydajności", "Uwierzytelniona JSON REST API", "Publiczna 0.7.3 planowana", "Workspace walidacji release"]},
                "intro": "eMule broadband edition, krótko <strong>eMule BB</strong>, to niezależna linia produktu dla osób, które nadal cenią rozproszony model eMule. Zachowuje klasyczne desktop workflows, a jednocześnie ułatwia uruchamianie, obserwowanie, automatyzowanie i walidowanie klienta na aktualnych systemach Windows.",
                "why": {**s("Dlaczego", "Klient legacy ma sens tylko wtedy, gdy można nim nadal pewnie zarządzać", "eMule BB to produkt i dyscyplina inżynierska: zachować natywną aplikację Windows z prawdziwym zachowaniem sieciowym oraz otoczyć ją nowoczesnym build, testami, dokumentacją, automatyzacją i procesem release."), "cards": [c("Powód produktowy", "Utrzymać eD2K i Kad w praktyce", "To nie nostalgia ani rewrite. Chodzi o utrzymanie klasycznego modelu dla długich sesji, rzadkich plików, świadomego seeding i użytkowników chcących natywnego klienta."), c("Powód techniczny", "Ujawnić stare założenia", "Defaults dotyczące upload slots, timeouts, buffers, dużych bibliotek i ekspozycji WebServer stają się jawne, testowalne i dokumentowalne."), c("Powód release", "Dowodzić legacy-code nowoczesnymi metodami", "Workspace traktuje release jako artefakt inżynierski: source policy, kontrakty OpenAPI, powtarzalne builds, hashes, live checks i operator gates muszą się zgadzać.")]},
                "features": {**s("Funkcje", "Co eMule BB dodaje wokół klasycznego klienta", "Praca skupia się na zachowaniu widocznym dla operatora: przewidywalny upload, bezpieczniejszy binding, stałe limity wydajności, duże biblioteki, lokalna automatyzacja i dowody dla planowanego release <code>0.7.3</code>."), "cards": [c("Udostępnianie i upload", "Kontrola uploadu na szybkich łączach", "Ograniczone cele slots, recykling słabych slots, odczyty ratio i kontrola seeding utrzymują szybki upload bez zmiany protokołu eD2K."), c("Kontrola sieci", "Binding, NAT i polityka ekspozycji", "Interface-aware binding, walidacja UPnP/NAT, HTTPS, allowed-IP rules i dziedziczenie WebServer utrzymują powierzchnie zdalne jawne i testowalne."), c("Wydajność i skala", "Aktualne defaults dla dużych sesji", "Większe socket buffers, limity queue/source, file buffering, timeouts, rekursywny sync i long paths są ukierunkowane na współczesny Windows i duże biblioteki."), c("Klasyczna sieć", "eD2K i Kad pozostają pierwsze", "Server, global i Kad search pozostają natywną podstawą, a Kad identity, bad-node handling, cleanup i timing mieszczą się w granicach zgodności."), c("Automatyzacja", "REST i controller workflows", "Uwierzytelnione JSON endpoints obejmują transfers, searches, shared files, servers, Kad, logs, categories, uploads, statistics, preferences i controlled shutdown."), c("Dyscyplina release", "Dowody przed publicznymi pakietami", "Beta <code>0.7.3</code> zależy od native tests, REST contracts, live controller lanes, network adversity, packaging i prób x64/ARM64.")]},
                "guide": {**s("Przewodnik produktu", "Krótki model pracy"), "cards": [c("", "Zacznij od dobrych nawyków eMule", "Używaj zaufanych server lists, uruchamiaj Kad świadomie, trzymaj incoming i shared folders przewidywalnie i zachowaj klasyczny workflow przed automatyzacją."), c("", "Dostosuj upload do realnego łącza", "Ustaw skończony upload limit, wybierz realistyczny cel klientów i pozwól broadband policy preferować mniej, ale mocniejszych slots."), c("", "Dbaj o duże biblioteki", "Używaj Windows z long paths, utrzymuj shared roots w porządku, obserwuj ratios i traktuj rzadkie pliki jak świadome publikacje."), c("", "Automatyzuj tylko w zaufanych sieciach", "Włącz WebServer/REST z API key, ostrożnie ustaw binding i firewall oraz używaj controllers szanujących natywną semantykę eMule."), c("", "Śledź gotowość release", "Traktuj publiczną branch jak aktywny pre-release, dopóki gates <code>0.7.3</code>, operator checks i live E2E evidence nie powiedzą inaczej."), c("", "Szczegóły są w dokumentacji", "Homepage pozostaje zwarta. Przewodnik produktu, kontrakt REST, notatki o broadband i dokumenty release są w Markdown w repozytorium tooling.")]},
                "automation": {"eyebrow": "Powierzchnia sterowania", "h2": "REST automation bez zastępowania aplikacji desktop", "p": "Linia broadband release udostępnia resource-oriented JSON API <code>/api/v1</code> przez istniejący listener WebServer. Uwierzytelnia przez <code>X-API-Key</code>, zwraca JSON envelopes i prowadzi zmiany stanu eMule przez aplikację.", "pills_label": "Obszary REST API", "pills": ["Transfers", "Searches", "Servers", "Kad", "Shared files", "Uploads", "Categories", "Logs", "Statistics", "Preferences"]},
                "release": {**s("Status wydania", "Publiczna wersja 0.7.3 jest planowana, ma gates i nie została jeszcze wydana"), "cards": [c("", "Aktualny status", "Pierwszy publiczny target to <code>0.7.3</code>. Nie został jeszcze wydany. Końcowy dowód jest wstrzymany decyzją operatora, a publiczny status pozostaje związany z aktywnymi dokumentami."), c("", "Dowód build i pakietu", "Dowód obejmuje workspace validation, Debug i Release x64 app builds, Release ARM64 app builds, test binaries, package generation, clean-worktree checks oraz SHA-256 hashes."), c("", "Dowód zachowania", "Gates obejmują native suites, REST contract, OpenAPI drift, malformed requests, UI automation, live controller-surface E2E, pełny Release x64 live E2E i network adversity."), c("", "Dowód controllers", "aMuTorrent, Prowlarr, Radarr, Sonarr i qBittorrent-compatible lanes pokazują automation bez osłabiania natywnego kontraktu <code>/api/v1</code>."), c("", "Dowód zgodności", "Oryginalne zachowanie eD2K/Kad pozostaje default. Broadband, REST i controllers są dodawane wokół tego celu zgodności.")]},
                "method": {**s("Metoda implementacji", "Modernizować wokół legacy-core, a potem dowieść wyniku", "Styl jest celowo konserwatywny. eMule BB zmienia lokalną policy, limits, diagnostics, API boundaries i release discipline, zachowując domyślną zgodność eD2K/Kad."), "cards": [c("Zgodność", "Bez przypadkowego protocol drift", "Zmiany Kad i eD2K zostają w local routing, timing, validation i control paths. Wire formats, opcodes i native workflows są granicami zgodności."), c("Limity", "Stałe, sprawdzalne defaults", "Nowoczesne założenia o bandwidth, memory, socket, queue i timeout są wyrażone jako jawne defaults albo advanced preferences."), c("REST", "Kontrakty sterowania, nie screen scraping", "Uwierzytelniona JSON API trzyma się kontraktu OpenAPI, odrzuca malformed inputs i prowadzi native state mutations przez aplikację."), c("Release", "Dowody przed etykietami", "Proces zapisuje commands, commits, logs, package paths, hashes, live evidence i operator decisions, aby tag był sprawdzonym wynikiem.")]},
                "repos": {**s("Publiczny workspace", "Główne repozytoria"), "links": []},
                "team": {**s("Kultura projektu", "Ludzie, którzy nie pozwalają queue stać się performancem"), "cards": [c("", "Terapeuta upload slots", "Daje słabym slots dokładnie tyle czasu na emocje, ile trzeba, po czym odsyła je do queue z formularzem i cooldown."), c("", "Archiwista bootstrap Kad", "Pilnuje świętej listy nodes, która zadziałała raz w 2007 roku i zasługuje na dobrze zweryfikowaną drugą szansę."), c("", "Bramkarz release gates", "Wpuszcza builds tylko wtedy, gdy przynoszą testy, live evidence i sensowne wyjaśnienie ostatniego socket.")]},
            },
        ),
        "nl": clone_base(
            "nl",
            {
                "title": "eMule broadband edition | eMule BB in het Nederlands",
                "meta_description": "eMule BB is een moderne eMule-editie voor breedband-uploadcontrole, VPN/interface binding, actuele prestatielimieten, grote gedeelde bibliotheken, REST automation, eD2K, Kad en geavanceerde workflows.",
                "og_title": "eMule broadband edition | eMule BB in het Nederlands",
                "og_description": "Moderne eMule voor uploadcontrole, VPN/interface binding, grote bibliotheken, REST automation, eD2K/Kad-compatibiliteit en release-validatie. De eerste publieke versie 0.7.3 is gepland en nog niet uitgebracht.",
                "structured_description": "Moderne eMule voor breedband-uploadcontrole, VPN/interface binding, grote gedeelde bibliotheken, REST automation, eD2K/Kad-compatibiliteit en geavanceerde workflows. De eerste publieke versie is gepland als 0.7.3 en nog niet uitgebracht.",
                "nav_label": "Hoofdnavigatie",
                "project_links_label": "Projectlinks",
                "product_summary_label": "Samenvatting van eMule BB",
                "footer_links_label": "Footerlinks",
                "nav": [{"id": "why", "label": "Waarom"}, {"id": "features", "label": "Functies"}, {"id": "guide", "label": "Gids"}, {"id": "docs", "label": "Documentatie"}, {"id": "automation", "label": "Automatisering"}, {"id": "release", "label": "Uitgave"}, {"id": "repos", "label": "Repositories"}],
                "hero": {"eyebrow": "Klassieke eMule, afgestemd op moderne breedband", "h1": "eMule BB houdt eD2K en Kad bruikbaar voor serieuze gebruikers.", "lead": "Een eMule voor power users met snelle uploads, grote gedeelde bibliotheken, altijd actieve Windows-sessies en lokale controller workflows zonder de vertrouwde desktop-app op te geven.", "source": "Broncode", "guide": "Productgids", "panel_kicker": "Producthouding", "panel_h2": "Behoudend waar compatibiliteit telt. Modern waar controle telt.", "panel_p": "eMule BB houdt de native eMule-workflow centraal en voegt breedbandgerichte queue-logica, lokale API-besturing en release-validatie toe.", "signals": ["Originele eD2K/Kad-compatibiliteit", "Controle over upload slots", "VPN/interface binding", "Actuele prestatielimieten", "Geauthenticeerde JSON REST API", "Publieke 0.7.3 gepland", "Workspace voor release-validatie"]},
                "intro": "eMule broadband edition, kortweg <strong>eMule BB</strong>, is een zelfstandige productlijn voor mensen die het gedistribueerde model van eMule nog steeds waardevol vinden. Het behoudt de klassieke desktop workflows en maakt de client beter uitvoerbaar, observeerbaar, automatiseerbaar en valideerbaar op moderne Windows-systemen.",
                "why": {**s("Waarom", "Een legacy-client is alleen nuttig als je hem nog met vertrouwen kunt beheren", "eMule BB is tegelijk productwerk en technische discipline: een native Windows-app met echt netwerkgedrag behouden en er moderne build, tests, documentatie, automatisering en release-proces omheen zetten."), "cards": [c("Productreden", "eD2K en Kad praktisch houden", "Het doel is geen nostalgie en geen rewrite. Het klassieke model moet bruikbaar blijven voor lange sessies, zeldzame bestanden, bewust seeding en gebruikers die nog een native client willen."), c("Technische reden", "Oude aannames zichtbaar maken", "Defaults rond upload slots, timeouts, buffers, grote bibliotheken en WebServer-blootstelling worden expliciet, zodat ze reviewbaar, testbaar en documenteerbaar zijn."), c("Release-reden", "Modern bewijs toepassen op legacy-code", "De workspace behandelt release als technisch artefact: source policy, OpenAPI-contracten, reproduceerbare builds, hashes, live checks en operator gates moeten kloppen.")]},
                "features": {**s("Functies", "Wat eMule BB rond de klassieke client toevoegt", "Het werk richt zich op gedrag dat de operator ziet: voorspelbare upload policy, veiliger binding, vaste prestatielimieten, grote bibliotheken, lokale automatisering en bewijs voor de geplande release <code>0.7.3</code>."), "cards": [c("Delen en upload", "Breedband-uploadcontrole", "Begrensde slotdoelen, hergebruik van zwakke slots, ratio-weergave en seeding controls houden snelle uploads nuttig zonder het eD2K-protocol te wijzigen."), c("Netwerkcontrole", "Binding, NAT en blootstellingsbeleid", "Interface-aware binding, UPnP/NAT-validatie, HTTPS, allowed-IP rules en WebServer-erfenis houden externe oppervlakken expliciet en testbaar."), c("Prestaties en schaal", "Actuele defaults voor grote sessies", "Grotere socket buffers, queue/source limits, file buffering, timeouts, recursieve sync en long paths richten zich op moderne Windows-systemen en grote bibliotheken."), c("Klassiek netwerk", "eD2K en Kad blijven eerst", "Server, globale en Kad search blijven de native basis, met Kad identity, bad-node handling, cleanup en timing binnen compatibiliteitsgrenzen."), c("Automatisering", "REST en controller workflows", "Geauthenticeerde JSON endpoints dekken transfers, searches, shared files, servers, Kad, logs, categories, uploads, statistics, preferences en controlled shutdown."), c("Release-discipline", "Bewijs vóór publieke pakketten", "De beta <code>0.7.3</code> hangt af van native tests, REST contracts, live controller lanes, network adversity, packaging en x64/ARM64-repetities.")]},
                "guide": {**s("Productgids", "Een kort gebruiksmodel"), "cards": [c("", "Begin met goede eMule-gewoonten", "Gebruik vertrouwde server lists, bootstrap Kad bewust, houd incoming en shared folders voorspelbaar en bewaar de klassieke workflow voor je automatiseert."), c("", "Stem upload af op je echte verbinding", "Stel een eindige upload limit in, kies een realistisch clientdoel en laat de breedband policy minder maar sterkere slots bevoordelen."), c("", "Beheer grote bibliotheken bewust", "Gebruik Windows met long paths, houd shared roots schoon, volg ratios en behandel zeldzame bestanden als bewuste publicatiekeuzes."), c("", "Automatiseer alleen op vertrouwde netwerken", "Schakel WebServer/REST in met API key, configureer binding en firewall zorgvuldig en gebruik controllers die native eMule-semantiek respecteren."), c("", "Volg release-gereedheid", "Behandel de publieke branch als actieve pre-release totdat <code>0.7.3</code>-gates, operator checks en live E2E evidence anders aangeven."), c("", "Gebruik de documentatie voor diepte", "De homepage blijft compact. Productgids, REST contract, breedbandnotities en release docs staan als Markdown in de tooling repository.")]},
                "automation": {"eyebrow": "Controller-oppervlak", "h2": "REST automation zonder de desktop-app te vervangen", "p": "De breedband release track biedt een resource-oriented JSON API <code>/api/v1</code> via de bestaande WebServer listener. De API authenticeert met <code>X-API-Key</code>, levert JSON envelopes en laat native eMule-statuswijzigingen via de app lopen.", "pills_label": "REST API-gebieden", "pills": ["Transfers", "Searches", "Servers", "Kad", "Shared files", "Uploads", "Categories", "Logs", "Statistics", "Preferences"]},
                "release": {**s("Release-status", "Publieke versie 0.7.3 is gepland, heeft gates en is nog niet uitgebracht"), "cards": [c("", "Huidige status", "Het eerste publieke doel is <code>0.7.3</code>. Het is nog niet uitgebracht. Het finale bewijs is gepauzeerd door operator-richting en de publieke status blijft gekoppeld aan actieve release docs."), c("", "Build- en pakketbewijs", "Het bewijs omvat workspace validation, Debug en Release x64 app builds, Release ARM64 app builds, test binaries, package generation, clean-worktree checks en SHA-256 hashes."), c("", "Gedragsbewijs", "De gates dekken native suites, REST contract, OpenAPI drift, malformed requests, UI automation, live controller-surface E2E, volledige Release x64 live E2E en network adversity."), c("", "Controller-bewijs", "aMuTorrent, Prowlarr, Radarr, Sonarr en qBittorrent-compatible lanes bewijzen automation zonder het native contract <code>/api/v1</code> te verzwakken."), c("", "Compatibiliteitsbewijs", "Origineel eD2K/Kad-gedrag blijft default. Breedband, REST en controllers worden rond dat compatibiliteitsdoel toegevoegd.")]},
                "method": {**s("Implementatiemethode", "Moderniseren rond de legacy-kern, daarna het resultaat bewijzen", "De stijl is bewust behoudend. eMule BB wijzigt lokale policy, limits, diagnostics, API boundaries en release discipline terwijl eD2K/Kad-compatibiliteit default blijft."), "cards": [c("Compatibiliteit", "Geen toevallige protocol drift", "Kad- en eD2K-wijzigingen blijven binnen local routing, timing, validation en control paths. Wire formats, opcodes en native workflows zijn compatibiliteitsgrenzen."), c("Limieten", "Vaste, reviewbare defaults", "Moderne aannames rond bandwidth, memory, socket, queue en timeout worden expliciete defaults of advanced preferences."), c("REST", "Controller-contracten, geen screen scraping", "De geauthenticeerde JSON API volgt een OpenAPI-contract, weigert malformed inputs en laat native state mutations via de app lopen."), c("Release", "Bewijs vóór labels", "Het proces registreert commands, commits, logs, package paths, hashes, live evidence en operator decisions zodat een tag een gecontroleerd resultaat is.")]},
                "repos": {**s("Publieke workspace", "Primaire repositories"), "links": []},
                "team": {**s("Projectcultuur", "De mensen die voorkomen dat de queue performancekunst wordt"), "cards": [c("", "Therapeut voor upload slots", "Laat zwakke slots precies lang genoeg hun gevoelens verwerken voordat ze met formulier en cooldown terug de queue in gaan."), c("", "Archivaris van Kad-bootstrap", "Bewaart de heilige lijst nodes die ooit in 2007 werkte en daarom een zorgvuldig gevalideerde tweede kans verdient."), c("", "Bewaker van release gates", "Laat builds alleen binnen met tests, live evidence en een overtuigende verklaring over de laatste socket.")]},
            },
        ),
        "tr": clone_base(
            "tr",
            {
                "title": "eMule broadband edition | Türkçe eMule BB",
                "meta_description": "eMule BB; geniş bant upload kontrolü, VPN/interface binding, güncel performans sınırları, büyük paylaşılan kütüphaneler, REST automation, eD2K, Kad ve ileri workflows için modern bir eMule sürümüdür.",
                "og_title": "eMule broadband edition | Türkçe eMule BB",
                "og_description": "Geniş bant upload kontrolü, VPN/interface binding, büyük kütüphaneler, REST automation, eD2K/Kad uyumluluğu ve release doğrulaması için modern eMule. İlk public sürüm 0.7.3 planlandı ve henüz yayınlanmadı.",
                "structured_description": "Geniş bant upload kontrolü, VPN/interface binding, büyük paylaşılan kütüphaneler, REST automation, eD2K/Kad uyumluluğu ve ileri workflows için modern eMule. İlk public sürüm 0.7.3 olarak planlandı ve henüz yayınlanmadı.",
                "nav_label": "Ana gezinme",
                "project_links_label": "Proje bağlantıları",
                "product_summary_label": "eMule BB özeti",
                "footer_links_label": "Alt bağlantılar",
                "nav": [{"id": "why", "label": "Neden"}, {"id": "features", "label": "Özellikler"}, {"id": "guide", "label": "Kılavuz"}, {"id": "docs", "label": "Belgeler"}, {"id": "automation", "label": "Otomasyon"}, {"id": "release", "label": "Yayın"}, {"id": "repos", "label": "Depolar"}],
                "hero": {"eyebrow": "Klasik eMule, modern geniş bant için ayarlandı", "h1": "eMule BB, eD2K ve Kad'i ciddi kullanıcılar için kullanışlı tutar.", "lead": "Hızlı upload bağlantıları, büyük paylaşılan kütüphaneler, sürekli açık Windows oturumları ve tanıdık desktop uygulamasından vazgeçmeden yerel controller workflows isteyen power user'lar için eMule.", "source": "Kaynak kod", "guide": "Ürün kılavuzu", "panel_kicker": "Ürün duruşu", "panel_h2": "Uyumluluğun önemli olduğu yerde tutucu. Kontrolün önemli olduğu yerde modern.", "panel_p": "eMule BB, native eMule workflow'u merkezde tutar; çevresine geniş bant queue davranışı, yerel API kontrolü ve release doğrulaması ekler.", "signals": ["Orijinal eD2K/Kad uyumluluğu", "Upload slot kontrolü", "VPN/interface binding", "Güncel performans sınırları", "Kimlik doğrulamalı JSON REST API", "Public 0.7.3 planlandı", "Release doğrulama workspace'i"]},
                "intro": "eMule broadband edition, kısaca <strong>eMule BB</strong>, eMule'un dağıtık paylaşım modeline hâlâ değer verenler için bağımsız bir ürün çizgisidir. Klasik desktop workflows korunur; istemci modern Windows sistemlerinde daha kolay çalıştırılır, gözlenir, otomatikleştirilir ve doğrulanır.",
                "why": {**s("Neden", "Legacy bir client ancak güvenle işletilebiliyorsa işe yarar", "eMule BB hem ürün çalışması hem de mühendislik disiplinidir: gerçek ağ davranışı olan native Windows uygulamasını korumak ve etrafına modern build, test, dokümantasyon, otomasyon ve release süreci koymak."), "cards": [c("Ürün nedeni", "eD2K ve Kad'i pratik tutmak", "Amaç nostalji ya da rewrite değil. Klasik modeli uzun oturumlar, nadir dosyalar, bilinçli seeding ve native client isteyen kullanıcılar için kullanışlı tutmaktır."), c("Teknik neden", "Eski varsayımları görünür yapmak", "Upload slots, timeouts, buffers, büyük kütüphaneler ve WebServer açıklığı için defaults görünür olur; review, test ve dokümantasyon yapılabilir."), c("Release nedeni", "Legacy code üstünde modern kanıt üretmek", "Workspace release'i mühendislik çıktısı olarak görür: source policy, OpenAPI contracts, tekrarlanabilir builds, hashes, live checks ve operator gates aynı çizgide olmalıdır.")]},
                "features": {**s("Özellikler", "eMule BB'nin klasik client etrafına ekledikleri", "Çalışma operatörün görebildiği davranışa odaklanır: öngörülebilir upload policy, daha güvenli binding, sabit performans sınırları, büyük kütüphaneler, yerel otomasyon ve planlanan <code>0.7.3</code> release için kanıt."), "cards": [c("Paylaşım ve upload", "Geniş bant upload kontrolü", "Sınırlı slot hedefleri, zayıf slot recycling, ratio göstergeleri ve seeding controls hızlı upload'u eD2K protokolünü değiştirmeden kullanışlı tutar."), c("Ağ kontrolü", "Binding, NAT ve açıklık politikası", "Interface-aware binding, UPnP/NAT doğrulaması, HTTPS, allowed-IP rules ve WebServer mirası uzak yüzeyleri açık ve test edilebilir tutar."), c("Performans ve ölçek", "Büyük oturumlar için güncel defaults", "Daha büyük socket buffers, queue/source limits, file buffering, timeouts, recursive sync ve long paths desteği modern Windows ve büyük kütüphaneleri hedefler."), c("Klasik ağ", "eD2K ve Kad önce gelir", "Server, global ve Kad search native temel olarak kalır; Kad identity, bad-node handling, cleanup ve timing uyumluluk sınırları içinde tutulur."), c("Otomasyon", "REST ve controller workflows", "Kimlik doğrulamalı JSON endpoints transfers, searches, shared files, servers, Kad, logs, categories, uploads, statistics, preferences ve controlled shutdown alanlarını kapsar."), c("Release disiplini", "Public paketlerden önce kanıt", "<code>0.7.3</code> beta; native tests, REST contracts, live controller lanes, network adversity, packaging ve x64/ARM64 provalarına bağlıdır.")]},
                "guide": {**s("Ürün kılavuzu", "Kısa işletim modeli"), "cards": [c("", "Bilinen iyi eMule alışkanlıklarından başla", "Güvenilir server lists kullan, Kad'i bilinçli başlat, incoming ve shared folders düzenli tut, otomasyon eklemeden önce klasik workflow'u koru."), c("", "Upload'u gerçek bağlantıya göre ayarla", "Sonlu bir upload limit belirle, gerçekçi bir client hedefi seç ve broadband policy'nin daha az ama daha güçlü slots tercih etmesine izin ver."), c("", "Büyük kütüphaneleri düzenli tut", "Long paths destekli Windows kullan, shared roots alanlarını temiz tut, ratios izle ve nadir dosyaları bilinçli yayın kararı olarak ele al."), c("", "Sadece güvenilen ağlarda otomatikleştir", "WebServer/REST'i API key ile aç, binding ve firewall'u dikkatle ayarla ve native eMule semantiğine saygılı controllers kullan."), c("", "Release hazırlığını izle", "Public branch'i, <code>0.7.3</code> gates, operator checks ve live E2E evidence aksini söyleyene kadar aktif pre-release kabul et."), c("", "Ayrıntılar için belgeleri kullan", "Homepage kısa kalır. Ürün kılavuzu, REST contract, broadband notları ve release docs tooling repository içinde Markdown olarak yaşar.")]},
                "automation": {"eyebrow": "Controller yüzeyi", "h2": "Desktop uygulamasını değiştirmeden REST automation", "p": "Broadband release track, mevcut WebServer listener üzerinden resource-oriented JSON API <code>/api/v1</code> sunar. <code>X-API-Key</code> ile kimlik doğrular, JSON envelopes döner ve native eMule state değişikliklerini uygulama üzerinden geçirir.", "pills_label": "REST API alanları", "pills": ["Transfers", "Searches", "Servers", "Kad", "Shared files", "Uploads", "Categories", "Logs", "Statistics", "Preferences"]},
                "release": {**s("Release durumu", "Public 0.7.3 planlandı, gates altında ve henüz yayınlanmadı"), "cards": [c("", "Güncel durum", "İlk public hedef <code>0.7.3</code>. Henüz yayınlanmadı. Final kanıt operatör yönlendirmesiyle duraklatıldı ve public durum aktif release docs'a bağlı kalır."), c("", "Build ve paket kanıtı", "Kanıt workspace validation, Debug ve Release x64 app builds, Release ARM64 app builds, test binaries, package generation, clean-worktree checks ve SHA-256 hashes kapsar."), c("", "Davranış kanıtı", "Gates native suites, REST contract, OpenAPI drift, malformed requests, UI automation, live controller-surface E2E, tam Release x64 live E2E ve network adversity kapsar."), c("", "Controller kanıtı", "aMuTorrent, Prowlarr, Radarr, Sonarr ve qBittorrent-compatible lanes, native <code>/api/v1</code> contract zayıflamadan automation çalıştığını gösterir."), c("", "Uyumluluk kanıtı", "Orijinal eD2K/Kad davranışı default kalır. Broadband, REST ve controllers bu uyumluluk hedefinin çevresine eklenir.")]},
                "method": {**s("Uygulama yöntemi", "Legacy çekirdeğin etrafında modernleştir, sonra sonucu kanıtla", "Stil bilinçli olarak tutucudur. eMule BB yerel policy, limits, diagnostics, API boundaries ve release discipline alanlarını değiştirirken eD2K/Kad uyumluluğunu default tutar."), "cards": [c("Uyumluluk", "Gelişigüzel protocol drift yok", "Kad ve eD2K değişiklikleri local routing, timing, validation ve control paths içinde kalır. Wire formats, opcodes ve native workflows uyumluluk sınırıdır."), c("Sınırlar", "Sabit ve review edilebilir defaults", "Bandwidth, memory, socket, queue ve timeout varsayımları gizli adaptif davranış yerine açık defaults veya advanced preferences olur."), c("REST", "Controller contracts, screen scraping değil", "Kimlik doğrulamalı JSON API OpenAPI-backed contract izler, malformed inputs reddeder ve native state mutations uygulama üzerinden yürütür."), c("Release", "Etiketlerden önce kanıt", "Süreç commands, commits, logs, package paths, hashes, live evidence ve operator decisions kaydeder; tag doğrulanmış bir sonuç olur.")]},
                "repos": {**s("Public workspace", "Ana depolar"), "links": []},
                "team": {**s("Proje kültürü", "Queue'nun performans sanatına dönüşmesini engelleyen ekip"), "cards": [c("", "Upload slot terapisti", "Zayıf slots duygularını tam gerektiği kadar işler, sonra form ve cooldown ile queue'ya geri gönderilir."), c("", "Kad bootstrap arşivcisi", "2007'de bir kez çalışan ve bu yüzden dikkatle doğrulanmış ikinci şansı hak eden nodes listesini korur."), c("", "Release gate görevlisi", "Builds yalnızca test, live evidence ve son socket hakkında makul açıklama getirdiğinde içeri girer.")]},
            },
        ),
    }
)


DOC_COPY = {
    "en": {
        "emulebb": ("eMule BB product guide", "Product overview for setup, tuning, automation, and release-aware use."),
        "setup": ("Setup guide", "Install model, first-run profile behavior, and practical startup notes."),
        "network": ("Network guide", "eD2K, Kad, binding, UPnP, firewall, and connection diagnosis reference."),
        "sharing": ("Sharing guide", "Shared directories, monitored shares, large libraries, and share policy files."),
        "downloads": ("Downloads and search guide", "Search modes, result trust, categories, and power-user file workflows."),
        "controllers": ("Controllers and REST guide", "Trusted local controller usage and automation boundaries."),
        "rest_contract": ("REST API contract", "Human-readable contract for the authenticated JSON control surface."),
        "rest_adapters": ("REST adapter contracts", "qBittorrent-compatible and Torznab adapter surface for controller authors."),
        "troubleshooting": ("Troubleshooting guide", "Symptom-led checks for Low ID, network issues, sharing, and automation."),
        "release": ("0.7.3 release dashboard", "Current planned beta gates, evidence pointers, and readiness rules."),
    },
    "es": {
        "emulebb": ("Guía de producto eMule BB", "Visión de conjunto para instalación, ajuste, automatización y uso atento al release."),
        "setup": ("Guía de instalación", "Modelo de instalación, primer perfil y notas prácticas de arranque."),
        "network": ("Guía de red", "Referencia de eD2K, Kad, binding, UPnP, firewall y diagnóstico de conexión."),
        "sharing": ("Guía de compartición", "Directorios compartidos, shares monitorizados, bibliotecas grandes y archivos de política."),
        "downloads": ("Guía de descargas y búsqueda", "Modos de búsqueda, confianza en resultados, categorías y workflows avanzados."),
        "controllers": ("Guía de controladores y REST", "Uso de controladores locales confiables y límites de automatización."),
        "rest_contract": ("Contrato REST API", "Contrato legible de la superficie JSON autenticada."),
        "rest_adapters": ("Contratos de adaptadores REST", "Superficie qBittorrent-compatible y Torznab para autores de controladores."),
        "troubleshooting": ("Guía de diagnóstico", "Comprobaciones por síntoma para Low ID, red, compartición y automatización."),
        "release": ("Panel de release 0.7.3", "Gates de beta planificados, evidencias y reglas de preparación."),
    },
    "pt_br": {
        "emulebb": ("Guia do produto eMule BB", "Visão geral para setup, ajuste, automação e uso atento ao release."),
        "setup": ("Guia de setup", "Modelo de instalação, perfil inicial e notas práticas de inicialização."),
        "network": ("Guia de rede", "Referência de eD2K, Kad, binding, UPnP, firewall e diagnóstico de conexão."),
        "sharing": ("Guia de compartilhamento", "Diretórios compartilhados, shares monitorados, bibliotecas grandes e arquivos de política."),
        "downloads": ("Guia de downloads e busca", "Modos de busca, confiança nos resultados, categorias e workflows avançados."),
        "controllers": ("Guia de controladores e REST", "Uso de controladores locais confiáveis e limites da automação."),
        "rest_contract": ("Contrato REST API", "Contrato legível da superfície JSON autenticada."),
        "rest_adapters": ("Contratos de adaptadores REST", "Superfície qBittorrent-compatible e Torznab para autores de controladores."),
        "troubleshooting": ("Guia de solução de problemas", "Checks por sintoma para Low ID, rede, compartilhamento e automação."),
        "release": ("Painel do release 0.7.3", "Gates planejados da beta, evidências e regras de prontidão."),
    },
    "pt_pt": {
        "emulebb": ("Guia do produto eMule BB", "Visão geral para setup, afinação, automação e uso atento ao release."),
        "setup": ("Guia de setup", "Modelo de instalação, perfil inicial e notas práticas de arranque."),
        "network": ("Guia de rede", "Referência de eD2K, Kad, binding, UPnP, firewall e diagnóstico de ligação."),
        "sharing": ("Guia de partilha", "Directórios partilhados, shares monitorizadas, bibliotecas grandes e ficheiros de política."),
        "downloads": ("Guia de downloads e pesquisa", "Modos de pesquisa, confiança nos resultados, categorias e workflows avançados."),
        "controllers": ("Guia de controladores e REST", "Uso de controladores locais fiáveis e limites da automação."),
        "rest_contract": ("Contrato REST API", "Contrato legível da superfície JSON autenticada."),
        "rest_adapters": ("Contratos de adaptadores REST", "Superfície qBittorrent-compatible e Torznab para autores de controladores."),
        "troubleshooting": ("Guia de resolução de problemas", "Checks por sintoma para Low ID, rede, partilha e automação."),
        "release": ("Painel do release 0.7.3", "Gates planeados da beta, evidências e regras de prontidão."),
    },
    "it": {
        "emulebb": ("Guida prodotto eMule BB", "Panoramica per setup, tuning, automazione e uso consapevole della release."),
        "setup": ("Guida di setup", "Modello di installazione, profilo iniziale e note pratiche di avvio."),
        "network": ("Guida rete", "Riferimento per eD2K, Kad, binding, UPnP, firewall e diagnosi connessione."),
        "sharing": ("Guida condivisione", "Directory condivise, share monitorate, grandi librerie e file di policy."),
        "downloads": ("Guida download e ricerca", "Modalità di ricerca, fiducia nei risultati, categorie e workflow avanzati."),
        "controllers": ("Guida controller e REST", "Uso di controller locali fidati e confini dell'automazione."),
        "rest_contract": ("Contratto REST API", "Contratto leggibile della superficie JSON autenticata."),
        "rest_adapters": ("Contratti adapter REST", "Superficie qBittorrent-compatible e Torznab per autori di controller."),
        "troubleshooting": ("Guida troubleshooting", "Controlli per sintomo su Low ID, rete, condivisione e automazione."),
        "release": ("Dashboard release 0.7.3", "Gate beta pianificati, riferimenti di prova e regole di prontezza."),
    },
    "ru": {
        "emulebb": ("Гайд по eMule BB", "Обзор setup, tuning, automation и использования с учетом release."),
        "setup": ("Гайд по setup", "Модель установки, первый профиль и практические заметки по запуску."),
        "network": ("Гайд по сети", "Справка по eD2K, Kad, binding, UPnP, firewall и диагностике соединений."),
        "sharing": ("Гайд по sharing", "Shared directories, monitored shares, большие библиотеки и policy files."),
        "downloads": ("Гайд по downloads и search", "Режимы search, доверие к результатам, categories и advanced workflows."),
        "controllers": ("Гайд по controllers и REST", "Использование доверенных локальных controllers и границы automation."),
        "rest_contract": ("Контракт REST API", "Читаемый контракт аутентифицированной JSON-поверхности управления."),
        "rest_adapters": ("Контракты REST adapters", "qBittorrent-compatible и Torznab поверхность для авторов controllers."),
        "troubleshooting": ("Гайд по troubleshooting", "Проверки по симптомам для Low ID, сети, sharing и automation."),
        "release": ("Панель release 0.7.3", "Запланированные beta gates, ссылки на evidence и правила готовности."),
    },
    "de": {
        "emulebb": ("eMule BB Produktguide", "Überblick für Setup, Tuning, Automatisierung und release-bewusste Nutzung."),
        "setup": ("Setup-Guide", "Installationsmodell, First-run-Profil und praktische Startnotizen."),
        "network": ("Netzwerk-Guide", "Referenz zu eD2K, Kad, binding, UPnP, Firewall und Verbindungsdiagnose."),
        "sharing": ("Freigabe-Guide", "Freigegebene Ordner, überwachte shares, große Bibliotheken und Policy-Dateien."),
        "downloads": ("Download- und Such-Guide", "Suchmodi, Vertrauen in Ergebnisse, Kategorien und Power-User-Workflows."),
        "controllers": ("Controller- und REST-Guide", "Nutzung vertrauenswürdiger lokaler Controller und Automatisierungsgrenzen."),
        "rest_contract": ("REST API Vertrag", "Lesbarer Vertrag für die authentifizierte JSON-Steuerfläche."),
        "rest_adapters": ("REST Adapter Verträge", "qBittorrent-compatible und Torznab Oberfläche für Controller-Autoren."),
        "troubleshooting": ("Troubleshooting-Guide", "Symptomgeführte Checks für Low ID, Netzwerk, Freigaben und Automatisierung."),
        "release": ("0.7.3 Release-Dashboard", "Geplante Beta-Gates, Evidenzverweise und Readiness-Regeln."),
    },
    "fr": {
        "emulebb": ("Guide produit eMule BB", "Vue d'ensemble pour setup, réglage, automatisation et usage attentif à la release."),
        "setup": ("Guide de setup", "Modèle d'installation, profil initial et notes pratiques de démarrage."),
        "network": ("Guide réseau", "Référence eD2K, Kad, binding, UPnP, firewall et diagnostic de connexion."),
        "sharing": ("Guide de partage", "Dossiers partagés, shares surveillés, grandes bibliothèques et fichiers de policy."),
        "downloads": ("Guide téléchargements et recherche", "Modes de recherche, confiance dans les résultats, catégories et workflows avancés."),
        "controllers": ("Guide contrôleurs et REST", "Usage de contrôleurs locaux fiables et limites d'automatisation."),
        "rest_contract": ("Contrat REST API", "Contrat lisible de la surface JSON authentifiée."),
        "rest_adapters": ("Contrats adaptateurs REST", "Surface qBittorrent-compatible et Torznab pour auteurs de contrôleurs."),
        "troubleshooting": ("Guide de dépannage", "Contrôles par symptôme pour Low ID, réseau, partage et automatisation."),
        "release": ("Tableau release 0.7.3", "Gates beta prévus, pointeurs de preuve et règles de préparation."),
    },
    "pl": {
        "emulebb": ("Przewodnik produktu eMule BB", "Omówienie setup, strojenia, automatyzacji i użycia świadomego release."),
        "setup": ("Przewodnik setup", "Model instalacji, pierwszy profil i praktyczne notatki startowe."),
        "network": ("Przewodnik sieci", "Referencja eD2K, Kad, binding, UPnP, firewall i diagnostyka połączeń."),
        "sharing": ("Przewodnik udostępniania", "Shared directories, monitored shares, duże biblioteki i pliki policy."),
        "downloads": ("Przewodnik pobierania i search", "Tryby search, zaufanie do wyników, kategorie i power-user workflows."),
        "controllers": ("Przewodnik controllers i REST", "Użycie zaufanych lokalnych controllers i granice automatyzacji."),
        "rest_contract": ("Kontrakt REST API", "Czytelny kontrakt uwierzytelnionej powierzchni JSON."),
        "rest_adapters": ("Kontrakty REST adapters", "qBittorrent-compatible i Torznab dla autorów controllers."),
        "troubleshooting": ("Przewodnik troubleshooting", "Kontrole objawowe dla Low ID, sieci, sharing i automatyzacji."),
        "release": ("Panel release 0.7.3", "Planowane beta gates, wskaźniki evidence i reguły gotowości."),
    },
    "nl": {
        "emulebb": ("eMule BB productgids", "Overzicht voor setup, tuning, automatisering en release-bewust gebruik."),
        "setup": ("Setupgids", "Installatiemodel, eerste profielgedrag en praktische startnotities."),
        "network": ("Netwerkgids", "Referentie voor eD2K, Kad, binding, UPnP, firewall en verbindingsdiagnose."),
        "sharing": ("Deelgids", "Shared directories, bewaakte shares, grote bibliotheken en policy files."),
        "downloads": ("Download- en zoekgids", "Zoekmodi, vertrouwen in resultaten, categorieën en power-user workflows."),
        "controllers": ("Controllers en REST-gids", "Gebruik van vertrouwde lokale controllers en automatiseringsgrenzen."),
        "rest_contract": ("REST API-contract", "Leesbaar contract voor het geauthenticeerde JSON-besturingsoppervlak."),
        "rest_adapters": ("REST adapter-contracten", "qBittorrent-compatible en Torznab oppervlak voor controller-auteurs."),
        "troubleshooting": ("Troubleshootinggids", "Symptoomgerichte checks voor Low ID, netwerk, delen en automatisering."),
        "release": ("0.7.3 release-dashboard", "Geplande beta gates, evidence pointers en gereedheidsregels."),
    },
    "tr": {
        "emulebb": ("eMule BB ürün kılavuzu", "Setup, tuning, automation ve release-bilinçli kullanım için genel bakış."),
        "setup": ("Setup kılavuzu", "Kurulum modeli, ilk profil davranışı ve pratik başlangıç notları."),
        "network": ("Ağ kılavuzu", "eD2K, Kad, binding, UPnP, firewall ve bağlantı tanısı referansı."),
        "sharing": ("Paylaşım kılavuzu", "Shared directories, monitored shares, büyük kütüphaneler ve policy files."),
        "downloads": ("Downloads ve search kılavuzu", "Search modları, sonuç güveni, categories ve power-user workflows."),
        "controllers": ("Controllers ve REST kılavuzu", "Güvenilir yerel controllers kullanımı ve automation sınırları."),
        "rest_contract": ("REST API contract", "Kimlik doğrulamalı JSON kontrol yüzeyi için okunabilir contract."),
        "rest_adapters": ("REST adapter contracts", "Controller yazarları için qBittorrent-compatible ve Torznab yüzeyi."),
        "troubleshooting": ("Troubleshooting kılavuzu", "Low ID, ağ, sharing ve automation için belirti odaklı checks."),
        "release": ("0.7.3 release paneli", "Planlanan beta gates, evidence bağlantıları ve readiness kuralları."),
    },
}

REPO_COPY = {
    "en": {"emule": "desktop app and product source", "setup": "reproducible workspace setup", "build": "build, validation, and release orchestration", "tests": "native, Python, UI, REST, and live E2E tests", "tooling": "roadmap, backlog, policy, audits, and reference docs"},
    "es": {"emule": "aplicación desktop y fuente del producto", "setup": "setup reproducible del workspace", "build": "orquestación de build, validación y release", "tests": "pruebas nativas, Python, UI, REST y live E2E", "tooling": "roadmap, backlog, políticas, auditorías y docs de referencia"},
    "pt_br": {"emule": "aplicativo desktop e fonte do produto", "setup": "setup reproduzível do workspace", "build": "orquestração de build, validação e release", "tests": "testes nativos, Python, UI, REST e live E2E", "tooling": "roadmap, backlog, políticas, auditorias e docs de referência"},
    "pt_pt": {"emule": "aplicação desktop e fonte do produto", "setup": "setup reproduzível do workspace", "build": "orquestração de build, validação e release", "tests": "testes nativos, Python, UI, REST e live E2E", "tooling": "roadmap, backlog, políticas, auditorias e docs de referência"},
    "it": {"emule": "app desktop e sorgente prodotto", "setup": "setup riproducibile del workspace", "build": "orchestrazione build, validazione e release", "tests": "test nativi, Python, UI, REST e live E2E", "tooling": "roadmap, backlog, policy, audit e documenti di riferimento"},
    "ru": {"emule": "desktop app и исходники продукта", "setup": "воспроизводимый setup workspace", "build": "build, validation и release orchestration", "tests": "native, Python, UI, REST и live E2E tests", "tooling": "roadmap, backlog, policy, audits и reference docs"},
    "de": {"emule": "Desktop-App und Produktquellen", "setup": "reproduzierbares Workspace-Setup", "build": "Build-, Validierungs- und Release-Orchestrierung", "tests": "native, Python-, UI-, REST- und live E2E-Tests", "tooling": "Roadmap, Backlog, Policy, Audits und Referenzdocs"},
    "fr": {"emule": "application desktop et source produit", "setup": "setup reproductible du workspace", "build": "orchestration build, validation et release", "tests": "tests natifs, Python, UI, REST et live E2E", "tooling": "roadmap, backlog, policy, audits et docs de référence"},
    "pl": {"emule": "aplikacja desktop i źródło produktu", "setup": "powtarzalny setup workspace", "build": "orkiestracja build, validation i release", "tests": "testy native, Python, UI, REST i live E2E", "tooling": "roadmap, backlog, policy, audits i reference docs"},
    "nl": {"emule": "desktop-app en productbron", "setup": "reproduceerbare workspace setup", "build": "build-, validatie- en release-orchestratie", "tests": "native, Python-, UI-, REST- en live E2E-tests", "tooling": "roadmap, backlog, policy, audits en referentiedocs"},
    "tr": {"emule": "desktop app ve ürün kaynağı", "setup": "tekrarlanabilir workspace setup", "build": "build, validation ve release orchestration", "tests": "native, Python, UI, REST ve live E2E tests", "tooling": "roadmap, backlog, policy, audits ve reference docs"},
}

DOC_SECTION_COPY = {
    "en": ("Read more", "Detailed guides and source documents"),
    "es": ("Más información", "Guías detalladas y documentos fuente"),
    "pt_br": ("Leia mais", "Guias detalhados e documentos-fonte"),
    "pt_pt": ("Ler mais", "Guias detalhados e documentos-fonte"),
    "it": ("Approfondisci", "Guide dettagliate e documenti sorgente"),
    "ru": ("Подробнее", "Подробные гайды и исходные документы"),
    "de": ("Mehr lesen", "Detaillierte Guides und Quelldokumente"),
    "fr": ("En savoir plus", "Guides détaillés et documents sources"),
    "pl": ("Więcej informacji", "Szczegółowe przewodniki i dokumenty źródłowe"),
    "nl": ("Meer lezen", "Gedetailleerde gidsen en brondocumenten"),
    "tr": ("Devamını oku", "Ayrıntılı kılavuzlar ve kaynak belgeler"),
}

REPO_SECTION_COPY = {
    "en": ("Public workspace", "Primary repositories"),
    "es": ("Workspace público", "Repositorios principales"),
    "pt_br": ("Workspace público", "Repositórios principais"),
    "pt_pt": ("Workspace público", "Repositórios principais"),
    "it": ("Workspace pubblico", "Repository principali"),
    "ru": ("Публичный workspace", "Основные репозитории"),
    "de": ("Öffentlicher Workspace", "Primäre Repositories"),
    "fr": ("Workspace public", "Dépôts principaux"),
    "pl": ("Publiczny workspace", "Główne repozytoria"),
    "nl": ("Publieke workspace", "Primaire repositories"),
    "tr": ("Açık workspace", "Ana depolar"),
}

MENU_COPY = {
    "en": {"label": "Menu", "open_label": "Open primary navigation", "close_label": "Close primary navigation"},
    "es": {"label": "Menú", "open_label": "Abrir navegación principal", "close_label": "Cerrar navegación principal"},
    "pt_br": {"label": "Menu", "open_label": "Abrir navegação principal", "close_label": "Fechar navegação principal"},
    "pt_pt": {"label": "Menu", "open_label": "Abrir navegação principal", "close_label": "Fechar navegação principal"},
    "it": {"label": "Menu", "open_label": "Apri navigazione principale", "close_label": "Chiudi navigazione principale"},
    "ru": {"label": "Меню", "open_label": "Открыть основную навигацию", "close_label": "Закрыть основную навигацию"},
    "de": {"label": "Menü", "open_label": "Hauptnavigation öffnen", "close_label": "Hauptnavigation schließen"},
    "fr": {"label": "Menu", "open_label": "Ouvrir la navigation principale", "close_label": "Fermer la navigation principale"},
    "pl": {"label": "Menu", "open_label": "Otwórz główną nawigację", "close_label": "Zamknij główną nawigację"},
    "nl": {"label": "Menu", "open_label": "Hoofdnavigatie openen", "close_label": "Hoofdnavigatie sluiten"},
    "tr": {"label": "Menü", "open_label": "Ana gezinmeyi aç", "close_label": "Ana gezinmeyi kapat"},
}


def with_generated_links() -> None:
    """Populate repeated docs and repo link sections for every locale."""

    for page in PAGES:
        content = CONTENT[page.key]
        content["menu"] = MENU_COPY[page.key]
        content["docs"]["eyebrow"], content["docs"]["h2"] = DOC_SECTION_COPY[page.key]
        content["docs"]["links"] = [
            {"href": href, "title": DOC_COPY[page.key][key][0], "text": DOC_COPY[page.key][key][1]}
            for href, key in DOCS
        ]
        content["repos"]["eyebrow"], content["repos"]["h2"] = REPO_SECTION_COPY[page.key]
        content["repos"]["links"] = [
            {"href": href, "title": title_for_repo(key), "text": REPO_COPY[page.key][key]}
            for href, key in REPOS
        ]


def title_for_repo(key: str) -> str:
    """Return the public repository display name for a repo key."""

    return {
        "emule": "eMule",
        "setup": "eMulebb-setup",
        "build": "eMule-build",
        "tests": "eMule-build-tests",
        "tooling": "eMule-tooling",
    }[key]


def to_namespace(value: Any) -> Any:
    """Recursively convert dictionaries so templates can use attribute access."""

    if isinstance(value, dict):
        return SimpleNamespace(**{key: to_namespace(item) for key, item in value.items()})
    if isinstance(value, list):
        return [to_namespace(item) for item in value]
    return value


def alternates() -> list[dict[str, str]]:
    """Return reciprocal hreflang alternates for generated pages."""

    result = [{"hreflang": page.hreflang, "url": page.url} for page in PAGES]
    result.append({"hreflang": "x-default", "url": f"{SITE_BASE_URL}/"})
    return result


def footer_links(page: PageSpec) -> list[dict[str, str]]:
    """Return footer language links relative to the generated page."""

    prefix = "" if page.directory == "" else "../"
    links = []
    for target in PAGES:
        if target.directory:
            href = f"{prefix}{target.directory}/"
        else:
            href = f"{prefix or './'}"
        links.append({"href": href, "label": target.language_label})
    return links


def environment(root: Path) -> Environment:
    """Create the Jinja2 environment for site rendering."""

    return Environment(
        loader=FileSystemLoader(root / "templates"),
        autoescape=select_autoescape(("html", "j2")),
        trim_blocks=False,
        lstrip_blocks=False,
    )


def render_sitemap(lastmod: str) -> str:
    """Render sitemap.xml from the canonical page table."""

    lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for page in PAGES:
        lines.extend(
            [
                "  <url>",
                f"    <loc>{page.url}</loc>",
                f"    <lastmod>{lastmod}</lastmod>",
                "    <changefreq>weekly</changefreq>",
                f"    <priority>{page.priority}</priority>",
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def render_outputs(root: Path, lastmod: str) -> dict[Path, str]:
    """Render every generated file into an in-memory path map."""

    with_generated_links()
    env = environment(root)
    home = env.get_template("home.html.j2")
    pt_selector = env.get_template("pt-selector.html.j2")
    alt = alternates()
    outputs: dict[Path, str] = {}
    for page in PAGES:
        outputs[page.output_path] = home.render(
            site_base_url=SITE_BASE_URL,
            pico_cdn=PICO_CDN,
            page=page,
            content=to_namespace(CONTENT[page.key]),
            alternates=alt,
            footer_locales=footer_links(page),
        )
    outputs[Path("pt") / "index.html"] = pt_selector.render(
        site_base_url=SITE_BASE_URL,
        pico_cdn=PICO_CDN,
        alternates=alt,
    )
    outputs[Path("sitemap.xml")] = render_sitemap(lastmod)
    return outputs


def write_outputs(root: Path, outputs: dict[Path, str], check: bool) -> int:
    """Write rendered files or fail when generated output differs."""

    failures = 0
    for relative, rendered in outputs.items():
        path = root / relative
        current = path.read_text(encoding="utf-8") if path.exists() else ""
        if current == rendered:
            continue
        if check:
            failures += 1
            print(f"{relative} is out of date", file=sys.stderr)
            diff = difflib.unified_diff(
                current.splitlines(),
                rendered.splitlines(),
                fromfile=f"{relative} (current)",
                tofile=f"{relative} (rendered)",
                lineterm="",
            )
            for line in list(diff)[:120]:
                print(line, file=sys.stderr)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"rendered {relative}")
    return 1 if failures else 0


def parse_args() -> argparse.Namespace:
    """Parse render command arguments."""

    parser = argparse.ArgumentParser(description="Render the eMule BB static pages.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--lastmod", default=dt.date.today().isoformat())
    parser.add_argument("--check", action="store_true", help="Fail if generated files differ.")
    return parser.parse_args()


def main() -> int:
    """Render or check the generated static pages."""

    args = parse_args()
    try:
        dt.date.fromisoformat(args.lastmod)
    except ValueError as exc:
        raise SystemExit(f"--lastmod must be an ISO date, got {args.lastmod!r}") from exc
    root = args.root.resolve()
    outputs = render_outputs(root, args.lastmod)
    return write_outputs(root, outputs, args.check)


if __name__ == "__main__":
    raise SystemExit(main())
