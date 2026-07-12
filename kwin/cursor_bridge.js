// Bridge KWin Scripting -> DBus para cursor-highlighter.
// Se carga dinamicamente via org.kde.kwin.Scripting.loadScript() al arrancar la app Python
// (ver src/cursor_highlighter/kwin_bridge/loader.py). No requiere kpackagetool6 ni reiniciar KWin.

function sendCursorMoved(x, y) {
    callDBus(
        "org.cursorhighlighter.App",
        "/org/cursorhighlighter/Bridge",
        "org.cursorhighlighter.Bridge1",
        "CursorMoved",
        x, y,
        function() {} // callDBus siempre es async y espera un callback, aunque no nos importe la reply
    );
}

function sendHotkeyTriggered(name) {
    callDBus(
        "org.cursorhighlighter.App",
        "/org/cursorhighlighter/Bridge",
        "org.cursorhighlighter.Bridge1",
        "HotkeyTriggered",
        name,
        function() {}
    );
}

workspace.cursorPosChanged.connect(function() {
    var pos = workspace.cursorPos;
    sendCursorMoved(pos.x, pos.y);
});

registerShortcut(
    "cursor-highlighter-toggle-highlight",
    "Cursor Highlighter: Toggle Highlight",
    "F8",
    function() {
        sendHotkeyTriggered("toggle_highlight");
    }
);

registerShortcut(
    "cursor-highlighter-next-profile",
    "Cursor Highlighter: Next Profile",
    "F9",
    function() {
        sendHotkeyTriggered("next_profile");
    }
);
