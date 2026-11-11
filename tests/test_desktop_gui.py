"""Presentation-adapter unit tests with real core/SQLite workers; real widgets are separately frozen-tested. Jason Stys."""
# BEGIN CODE MAP (generated; python scripts/code_map.py)
# definition: Variable — line 244
# definition: __init__ — line 247
# parameter: self — line 247
# parameter: value — line 247
# attribute: callbacks — line 249
# attribute: value — line 249
# definition: get — line 251
# parameter: self — line 251
# definition: set — line 255
# parameter: self — line 255
# parameter: value — line 255
# attribute: value — line 257
# variable: callback — line 258
# definition: trace_add — line 261
# parameter: _event — line 261
# parameter: callback — line 261
# parameter: self — line 261
# definition: Widget — line 266
# definition: __init__ — line 269
# parameter: _args — line 269
# parameter: kwargs — line 269
# parameter: self — line 269
# attribute: options — line 271
# attribute: rows — line 271
# attribute: selected — line 271
# attribute: flags — line 272
# attribute: tk — line 273
# parameter: _items — line 273
# definition: pack — line 275
# parameter: _kwargs — line 275
# parameter: self — line 275
# definition: grid — line 278
# parameter: _kwargs — line 278
# parameter: self — line 278
# definition: grid_remove — line 281
# parameter: self — line 281
# definition: columnconfigure — line 284
# parameter: _args — line 284
# parameter: _kwargs — line 284
# parameter: self — line 284
# definition: add — line 287
# parameter: _args — line 287
# parameter: _kwargs — line 287
# parameter: self — line 287
# definition: theme_use — line 290
# parameter: _args — line 290
# parameter: self — line 290
# definition: configure — line 293
# parameter: _args — line 293
# parameter: kwargs — line 293
# parameter: self — line 293
# definition: heading — line 297
# parameter: _args — line 297
# parameter: _kwargs — line 297
# parameter: self — line 297
# definition: column — line 300
# parameter: _args — line 300
# parameter: _kwargs — line 300
# parameter: self — line 300
# definition: bind — line 303
# parameter: _args — line 303
# parameter: self — line 303
# definition: yview — line 306
# parameter: _args — line 306
# parameter: self — line 306
# definition: set — line 309
# parameter: _args — line 309
# parameter: self — line 309
# definition: state — line 312
# parameter: flags — line 312
# parameter: self — line 312
# variable: flag — line 314
# definition: invoke — line 320
# parameter: self — line 320
# definition: insert — line 326
# parameter: _parent — line 326
# parameter: _position — line 326
# parameter: iid — line 326
# parameter: self — line 326
# parameter: values — line 326
# definition: delete — line 330
# parameter: items — line 330
# parameter: self — line 330
# variable: item — line 332
# attribute: selected — line 334
# variable: item — line 334
# definition: get_children — line 336
# parameter: self — line 336
# definition: selection — line 340
# parameter: self — line 340
# definition: selection_set — line 344
# parameter: identity — line 344
# parameter: self — line 344
# attribute: selected — line 347
# definition: Text — line 350
# definition: delete — line 353
# parameter: _args — line 353
# parameter: self — line 353
# attribute: text — line 355
# definition: insert — line 357
# parameter: _position — line 357
# parameter: self — line 357
# parameter: text — line 357
# attribute: text — line 359
# definition: Root — line 362
# definition: __init__ — line 365
# parameter: self — line 365
# attribute: callbacks — line 367
# attribute: destroyed — line 367
# attribute: on_loop — line 368
# definition: title — line 370
# parameter: _args — line 370
# parameter: self — line 370
# definition: geometry — line 373
# parameter: _args — line 373
# parameter: self — line 373
# definition: minsize — line 376
# parameter: _args — line 376
# parameter: self — line 376
# definition: protocol — line 379
# parameter: _event — line 379
# parameter: callback — line 379
# parameter: self — line 379
# attribute: close_callback — line 381
# definition: after — line 383
# parameter: _delay — line 383
# parameter: callback — line 383
# parameter: self — line 383
# definition: destroy — line 387
# parameter: self — line 387
# attribute: destroyed — line 389
# definition: mainloop — line 391
# parameter: self — line 391
# variable: _ — line 395
# definition: presentation — line 403
# parameter: monkeypatch — line 403
# parameter: _parent — line 408
# variable: name — line 410
# variable: messages — line 424
# parameter: _kwargs — line 426
# parameter: args — line 426
# parameter: _kwargs — line 429
# parameter: args — line 429
# definition: app — line 435
# parameter: presentation — line 435
# parameter: tmp_path — line 435
# variable: state — line 437
# variable: root — line 438
# variable: window — line 439
# definition: settle — line 453
# parameter: window — line 453
# variable: deadline — line 455
# definition: test_real_controller_run_filter_detail_history_export_and_help — line 462
# parameter: app — line 463
# parameter: monkeypatch — line 463
# parameter: presentation — line 463
# parameter: tmp_path — line 463
# parameter: _kwargs — line 489
# variable: original — line 491
# variable: exported — line 493
# variable: path — line 494
# parameter: _kwargs — line 499
# definition: test_explicit_retention_confirmation_removes_only_selected_local_copy — line 505
# parameter: app — line 506
# parameter: monkeypatch — line 506
# parameter: tmp_path — line 506
# variable: exported — line 516
# variable: original — line 517
# parameter: _args — line 518
# parameter: _kwargs — line 518
# parameter: _args — line 521
# parameter: _kwargs — line 521
# variable: path — line 524
# attribute: busy — line 525
# attribute: busy — line 528
# definition: test_input_selection_cancel_busy_failure_and_literal_row_cap — line 531
# parameter: app — line 532
# parameter: monkeypatch — line 532
# parameter: tmp_path — line 532
# variable: name — line 535
# parameter: _kwargs — line 539
# parameter: _kwargs — line 544
# parameter: _kwargs — line 547
# variable: kind — line 549
# variable: value — line 553
# parameter: _kwargs — line 554
# attribute: busy — line 557
# attribute: busy — line 563
# attribute: current — line 570
# variable: index — line 580
# definition: test_close_retains_lock_until_actual_core_transaction_finishes — line 594
# parameter: app — line 595
# parameter: monkeypatch — line 595
# parameter: tmp_path — line 595
# variable: ready — line 598
# variable: release — line 598
# variable: actual — line 599
# definition: pause — line 601
# parameter: args — line 601
# variable: reopened — line 619
# definition: test_main_native_close_and_rejected_acceptance_paths — line 626
# parameter: monkeypatch — line 627
# parameter: presentation — line 627
# parameter: tmp_path — line 627
# variable: actual — line 630
# definition: create — line 632
# parameter: root — line 632
# parameter: state — line 632
# variable: window — line 634
# attribute: on_loop — line 635
# variable: profile — line 639
# variable: reopened — line 641
# variable: unknown — line 665
# definition: test_prepared_mode_does_not_read_or_retain_inactive_selected_script — line 673
# parameter: app — line 674
# parameter: monkeypatch — line 674
# parameter: tmp_path — line 674
# variable: source — line 677
# variable: original — line 678
# attribute: visible — line 683
# variable: captured — line 686
# variable: save — line 687
# definition: record — line 689
# parameter: files — line 689
# parameter: kind — line 689
# parameter: parameters — line 689
# parameter: summary — line 689
# END CODE MAP

import threading
import time
from types import SimpleNamespace

import pytest

from rotation import desktop as module
from rotation import desktop_project as project
from rotation.desktop_io import Rejected
from rotation.desktop_state import Workspace


class Variable:
    """Inert presentation variable; invokes the same registered GUI trace callbacks."""

    def __init__(self, value=""):
        """Keep a scalar control value and registered change callbacks."""
        self.value, self.callbacks = value, []

    def get(self):
        """Return the current presentation control value."""
        return self.value

    def set(self, value):
        """Change a control and exercise actual application rendering callbacks."""
        self.value = value
        for callback in self.callbacks:
            callback()

    def trace_add(self, _event, callback):
        """Retain the GUI's value-change handler."""
        self.callbacks.append(callback)


class Widget:
    """Minimal inert ttk presentation adapter; no core, storage or analysis output is mocked."""

    def __init__(self, *_args, **kwargs):
        """Retain properties, rows and command closures."""
        self.options, self.rows, self.selected = kwargs, {}, ()
        self.flags = set()
        self.tk = SimpleNamespace(call=lambda *_items: None)

    def pack(self, **_kwargs):
        """Accept presentation layout."""

    def grid(self, **_kwargs):
        """Accept presentation grid coordinates."""

    def grid_remove(self):
        """Accept operation-specific hidden controls."""

    def columnconfigure(self, *_args, **_kwargs):
        """Accept resize weights."""

    def add(self, *_args, **_kwargs):
        """Accept notebook/paned-window children."""

    def theme_use(self, *_args):
        """Accept native style selection."""

    def configure(self, *_args, **kwargs):
        """Retain updated widget options."""
        self.options.update(kwargs)

    def heading(self, *_args, **_kwargs):
        """Accept a literal table heading."""

    def column(self, *_args, **_kwargs):
        """Accept table sizing."""

    def bind(self, *_args):
        """Accept event registration; tests invoke actual handlers explicitly."""

    def yview(self, *_args):
        """Accept scroll requests."""

    def set(self, *_args):
        """Accept scrollbar position updates."""

    def state(self, flags):
        """Preserve disabled controls so a simulated click cannot bypass a busy guard."""
        for flag in flags:
            if flag.startswith("!"):
                self.flags.discard(flag[1:])
            else:
                self.flags.add(flag)

    def invoke(self):
        """Invoke the actual registered command unless the control is disabled."""
        if "disabled" not in self.flags:
            return self.options["command"]()
        return None

    def insert(self, _parent, _position, *, iid, values):
        """Retain exact rows inserted by real project rendering."""
        self.rows[iid] = values

    def delete(self, *items):
        """Remove rows and their selections like a real treeview."""
        for item in items:
            self.rows.pop(item, None)
        self.selected = tuple(item for item in self.selected if item in self.rows)

    def get_children(self):
        """Return displayed row identities."""
        return tuple(self.rows)

    def selection(self):
        """Return the current selected row identity."""
        return self.selected

    def selection_set(self, identity):
        """Select one existing row like a real single-selection control."""
        assert identity in self.rows
        self.selected = (identity,)


class Text(Widget):
    """Retain literal detail output without interpreting markup or executing event fields."""

    def delete(self, *_args):
        """Clear existing literal detail text."""
        self.text = ""

    def insert(self, _position, text):
        """Retain the exact rendered detail text."""
        self.text = text


class Root:
    """Deterministic presentation event queue; actual Tk mainloops are independently exercised by frozen acceptance."""

    def __init__(self):
        """Create a fresh owned presentation root."""
        self.callbacks, self.destroyed = [], False
        self.on_loop = None

    def title(self, *_args):
        """Accept window title."""

    def geometry(self, *_args):
        """Accept initial geometry."""

    def minsize(self, *_args):
        """Accept minimum geometry."""

    def protocol(self, _event, callback):
        """Keep the application's native close callback."""
        self.close_callback = callback

    def after(self, _delay, callback):
        """Queue the actual lifecycle callback without a platform display server."""
        self.callbacks.append(callback)

    def destroy(self):
        """Mark only this owned root as closed."""
        self.destroyed = True

    def mainloop(self):
        """Run the requested test lifecycle using real application callbacks."""
        if self.on_loop:
            self.on_loop()
        for _ in range(200):
            if self.destroyed:
                return
            self.callbacks.pop(0)()
        raise AssertionError("presentation lifecycle did not close")


@pytest.fixture
def presentation(monkeypatch):
    """Replace only OS presentation surfaces; real worker, core, SQLite and export code remain active."""
    monkeypatch.setattr(module.tk, "StringVar", Variable)
    monkeypatch.setattr(module.tk, "BooleanVar", Variable)
    monkeypatch.setattr(module.tk, "Tk", Root)
    monkeypatch.setattr(module.tk, "Toplevel", lambda _parent: Root())
    monkeypatch.setattr(module.tk, "Text", Text)
    for name in (
        "Frame",
        "Label",
        "Notebook",
        "Combobox",
        "Entry",
        "Button",
        "Checkbutton",
        "Panedwindow",
        "Treeview",
        "Scrollbar",
        "Style",
    ):
        monkeypatch.setattr(module.ttk, name, Widget)
    messages = []
    monkeypatch.setattr(
        module.messagebox, "showinfo", lambda *args, **_kwargs: messages.append(args)
    )
    monkeypatch.setattr(
        module.messagebox, "showerror", lambda *args, **_kwargs: messages.append(args)
    )
    return messages


@pytest.fixture
def app(tmp_path, presentation):
    """Build the actual workbench controller against an isolated real durable workspace."""
    state = Workspace(tmp_path / "profile", project.PRODUCT, project.ROOT)
    root = Root()
    window = module.Workbench(root, state)
    # Presentation tests exercise the real offline domain engine and SQLite;
    # actual widgets/mainloop are separately proved by the final frozen consumer.
    window.prepared.set(project.SCENARIOS[1])
    window.load_prepared()
    try:
        yield window
    finally:
        if window.worker_thread:
            window.worker_thread.join(10)
            assert not window.worker_thread.is_alive()
        state.close()


def settle(window):
    """Observe completion of one actual owned analysis; no retries or invented report values."""
    deadline = time.monotonic() + 10
    while window.busy and time.monotonic() < deadline:
        window.poll()
        time.sleep(0.005)
    assert not window.busy


def test_real_controller_run_filter_detail_history_export_and_help(
    app, tmp_path, monkeypatch, presentation
):
    """Real core results drive controls, literal filters, exact private exports and history reopening."""
    app.export()
    assert "completed" in app.status.get()
    app.run_button.invoke()
    assert not app.busy and app.state.history() == []
    app.authorized.set(True)
    app.run_button.invoke()
    settle(app)
    assert app.selected_run == 1 and len(app.state.history()) == 1
    assert len(app.table.get_children()) > 0
    app.table.selection_set("0")
    app.inspect()
    assert "{" in app.details.text
    app.review_selected()
    if project.REVIEW_MODE is not None:
        assert app.mode.get() == project.REVIEW_MODE and app.authorized.get() is False
    app.search.set("not-a-supported-record-never-present")
    assert app.table.get_children() == ()
    app.inspect()
    app.search.set("")
    app.history_table.selection_set("1")
    app.open_button.invoke()
    assert "without re-running" in app.status.get()
    monkeypatch.setattr(
        module.filedialog, "askdirectory", lambda **_kwargs: str(tmp_path)
    )
    original = app.state.files(1)
    app.export_button.invoke()
    exported = next(tmp_path.glob(project.PRODUCT + "-run-*"))
    assert {path.name: path.read_bytes() for path in exported.iterdir()} == original
    app.help()
    assert "plaintext" in presentation[-1][1]
    app.licenses()
    monkeypatch.setattr(
        module.filedialog, "askdirectory", lambda **_kwargs: str(tmp_path / "missing")
    )
    app.export()
    assert "unavailable" in app.status.get()


def test_explicit_retention_confirmation_removes_only_selected_local_copy(
    app, tmp_path, monkeypatch
):
    """Cancellation preserves data; confirmation deletes one exact DB bundle without touching a prior export."""
    app.remove_history()
    assert "Select" in app.status.get()
    app.review_selected()
    app.authorized.set(True)
    app.run_button.invoke()
    settle(app)
    app.history_table.selection_set("1")
    exported = app.state.export(1, tmp_path, project.PRODUCT)
    original = app.state.files(1)
    monkeypatch.setattr(module.messagebox, "askyesno", lambda *_args, **_kwargs: False)
    app.remove_button.invoke()
    assert app.state.files(1) == original
    monkeypatch.setattr(module.messagebox, "askyesno", lambda *_args, **_kwargs: True)
    app.remove_button.invoke()
    assert app.state.history() == [] and app.selected_run == 0
    assert {path.name: path.read_bytes() for path in exported.iterdir()} == original
    app.busy = True
    app.remove_history()
    assert "Wait" in app.status.get()
    app.busy = False


def test_input_selection_cancel_busy_failure_and_literal_row_cap(
    app, tmp_path, monkeypatch
):
    """Operator mistakes do not silently run a prepared fixture, overwrite results or defeat close semantics."""
    name = "script"
    monkeypatch.setattr(
        module.filedialog,
        "askopenfilename",
        lambda **_kwargs: str(tmp_path / "authorized.json"),
    )
    monkeypatch.setattr(
        module.filedialog,
        "askopenfilenames",
        lambda **_kwargs: ("one.json", "two.json"),
    )
    monkeypatch.setattr(
        module.filedialog, "askdirectory", lambda **_kwargs: str(tmp_path)
    )
    for kind in ("file", "files", "directory"):
        app.authorized.set(True)
        app.choose(name, kind)
        assert app.authorized.get() is False
    value = app.values[name].get()
    monkeypatch.setattr(module.filedialog, "askopenfilename", lambda **_kwargs: "")
    app.choose(name, "file")
    assert app.values[name].get() == value
    app.busy = True
    app.choose(name, "file")
    app.load_prepared()
    app.open_history()
    app.run()
    assert app.state.history() == []
    app.busy = False
    app.load_prepared()
    app.mode.set("unsupported-operation")
    app.authorized.set(True)
    app.run()
    settle(app)
    assert "rejected" in app.status.get().lower() and app.state.history() == []
    app.current = {
        "bounded": [
            {
                "kind": "consumer",
                "consumer": str(index),
                "current_generation": 2,
                "requested_generation": 1,
                "acknowledged_generation": 0,
                "current_acknowledged": False,
            }
            for index in range(5001)
        ]
    }
    app.view.set("bounded")
    app.render()
    assert len(app.table.get_children()) == 5000
    app.search.set('"5000"')
    assert len(app.table.get_children()) == 1
    app.exit()
    app.run()
    app.poll()
    assert app.root.destroyed and app.state.lock == -1


def test_close_retains_lock_until_actual_core_transaction_finishes(
    app, tmp_path, monkeypatch
):
    """An in-flight real analysis is drained rather than abandoned, force-killed or exposed to a second owner."""
    ready, release = threading.Event(), threading.Event()
    actual = project.analyze

    def pause(*args):
        """Control only scheduling; completion still invokes the actual project core and durable output."""
        ready.set()
        assert release.wait(5)
        return actual(*args)

    monkeypatch.setattr(project, "analyze", pause)
    app.authorized.set(True)
    app.run_button.invoke()
    assert ready.wait(3)
    app.exit()
    app.poll()
    assert not app.root.destroyed and app.busy
    with pytest.raises((Rejected, OSError)):
        Workspace(app.state.path, project.PRODUCT, project.ROOT)
    release.set()
    settle(app)
    assert app.root.destroyed and app.state.lock == -1
    reopened = Workspace(app.state.path, project.PRODUCT, project.ROOT)
    try:
        assert len(reopened.history()) == 1
    finally:
        reopened.close()


def test_main_native_close_and_rejected_acceptance_paths(
    tmp_path, presentation, monkeypatch
):
    """Normal startup never auto-analyzes; test flags cannot enter existing real-profile state or claim partial success."""
    actual = module.Workbench

    def create(root, state):
        """Use actual controls/controller; request the normal close callback at the start of the event loop."""
        window = actual(root, state)
        root.on_loop = window.exit
        return window

    monkeypatch.setattr(module, "Workbench", create)
    profile = tmp_path / "normal"
    assert module.main(["--profile", str(profile)]) == 0
    reopened = Workspace(profile, project.PRODUCT, project.ROOT)
    assert reopened.history() == []
    reopened.close()
    with pytest.raises(SystemExit):
        module.main(["--acceptance-output", str(tmp_path / "output")])
    with pytest.raises(SystemExit):
        module.main(["--acceptance-reopen"])
    assert (
        module.main(
            ["--profile", str(profile), "--acceptance-output", str(tmp_path / "output")]
        )
        == 2
    )
    assert (
        module.main(
            [
                "--profile",
                str(tmp_path / "synthetic"),
                "--acceptance-output",
                str(tmp_path / "new-output"),
            ]
        )
        == 2
    )
    unknown = tmp_path / "unknown"
    unknown.mkdir()
    (unknown / "keep").write_bytes(b"unchanged")
    assert module.main(["--profile", str(unknown)]) == 2
    assert (unknown / "keep").read_bytes() == b"unchanged"
    assert presentation and "No saved evidence was reset" in presentation[-1][1]


def test_prepared_mode_does_not_read_or_retain_inactive_selected_script(
    app, tmp_path, monkeypatch
):
    """Switching to a prepared rehearsal cannot reuse an invisible script or prior result row."""
    source = tmp_path / "not-a-script.json"
    original = b"private prior input that is not a valid rehearsal"
    source.write_bytes(original)
    app.mode.set(project.MODES[1])
    app.values["exercise"].set("initial-handoff")
    app.values["script"].set(str(source))
    app.visible = [{"prior_selected_record": "not current input"}]
    app.table.insert("", "end", iid="0", values=("old",))
    app.table.selection_set("0")
    captured = []
    save = app.state.save

    def record(kind, summary, parameters, files):
        """Observe actual committed parameters without replacing the domain engine or durable save."""
        captured.append(dict(parameters))
        return save(kind, summary, parameters, files)

    monkeypatch.setattr(app.state, "save", record)
    app.authorized.set(True)
    app.run_button.invoke()
    settle(app)
    assert app.selected_run == 1 and len(captured) == 1
    assert set(captured[0]) == {"mode", *project.ACTIVE_FIELDS[project.MODES[1]]}
    assert "script" not in captured[0] and "_row" not in captured[0]
    assert source.read_bytes() == original
    assert b'"generation":1' in app.state.files(1)["handoff-rehearsal.json"]
