"""Write the KiCad project file and project library tables (JLCPCB 2-layer rules)."""
import json, os

D = os.path.join(os.path.dirname(__file__), '..')
P = 'intent-2026-badge'


def nc(name, track, clr=0.15, via_d=0.6, via_h=0.3, dp_w=0.25, dp_g=0.2):
    return {"name": name, "clearance": clr, "track_width": track, "via_diameter": via_d, "via_drill": via_h,
            "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": dp_w, "diff_pair_gap": dp_g,
            "diff_pair_via_gap": 0.25, "wire_width": 6, "bus_width": 12, "line_style": 0,
            "schematic_color": "rgba(0, 0, 0, 0.000)", "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647}


pro = {
    "board": {
        "design_settings": {
            "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2, "copper_text_size_h": 1.5,
                         "copper_text_size_v": 1.5, "copper_text_thickness": 0.3, "silk_line_width": 0.15,
                         "silk_text_size_h": 1.0, "silk_text_size_v": 1.0, "silk_text_thickness": 0.15,
                         "fab_line_width": 0.1, "other_line_width": 0.1, "courtyard_line_width": 0.05,
                         "pads": {"drill": 0.0, "height": 1.0, "width": 1.0}, "zones": {"min_clearance": 0.25}},
            "rules": {"min_clearance": 0.15, "min_track_width": 0.15, "min_connection": 0.15,
                      "min_via_diameter": 0.45, "min_via_annular_width": 0.075, "min_through_hole_diameter": 0.3,
                      "min_microvia_diameter": 0.2, "min_microvia_drill": 0.1, "min_hole_to_hole": 0.5,
                      "min_hole_clearance": 0.25, "min_copper_edge_clearance": 0.3, "min_silk_clearance": 0.0,
                      "min_text_height": 0.8, "min_text_thickness": 0.15, "min_resolved_spokes": 1,
                      "solder_mask_to_copper_clearance": 0.0, "use_height_for_length_calcs": True,
                      "allow_blind_buried_vias": False, "allow_microvias": False, "max_error": 0.005,
                      "solder_mask_clearance": 0.0, "solder_mask_min_width": 0.0},
            "track_widths": [0.0, 0.2, 0.3, 0.4, 0.6, 0.8],
            "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.6, "drill": 0.3}, {"diameter": 0.5, "drill": 0.3}],
            "diff_pair_dimensions": [{"width": 0.0, "gap": 0.0, "via_gap": 0.0}, {"width": 0.25, "gap": 0.2, "via_gap": 0.25}],
            "drc_exclusions": [],
            "rule_severities": {"silk_over_copper": "warning", "silk_overlap": "ignore", "silk_edge_clearance": "warning",
                                "text_height": "warning", "text_thickness": "warning", "lib_footprint_mismatch": "ignore",
                                "lib_footprint_issues": "ignore", "footprint_type_mismatch": "ignore",
                                "courtyards_overlap": "warning", "missing_courtyard": "ignore"},
        },
        "layer_presets": [], "viewports": [],
    },
    "boards": [],
    "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
    "meta": {"filename": P + ".kicad_pro", "version": 3},
    "net_settings": {
        "classes": [nc("Default", 0.2), nc("Power", 0.6), nc("Rail3V3", 0.4), nc("USB", 0.25)],
        "meta": {"version": 4},
        "netclass_assignments": None,
        "netclass_patterns": [
            {"netclass": "Power", "pattern": "VBUS"}, {"netclass": "Power", "pattern": "VSYS"},
            {"netclass": "Power", "pattern": "BAT_*"},
            {"netclass": "Rail3V3", "pattern": "+3V3"}, {"netclass": "Rail3V3", "pattern": "+1V1"},
            {"netclass": "USB", "pattern": "USB_D*"},
        ],
    },
    "pcbnew": {"last_paths": {}, "page_layout_descr_file": ""},
    "schematic": {"drawing": {"default_line_thickness": 6.0, "default_text_size": 50.0},
                  "erc_exclusions": [], "meta": {"version": 0}, "page_layout_descr_file": "",
                  "subpart_first_id": 65, "subpart_id_separator": 0},
    "sheets": [["6f6b0d3d-0000-0000-0000-000000000000", "Root"]],
    "text_variables": {"REV": "0.5", "EVENT": "INTENT 2026"},
}

if __name__ == '__main__':
    with open(os.path.join(D, P + '.kicad_pro'), 'w', newline='\n') as f:
        json.dump(pro, f, indent=2)
    with open(os.path.join(D, 'fp-lib-table'), 'w', newline='\n') as f:
        f.write('(fp_lib_table\n  (version 7)\n  (lib (name "intent")(type "KiCad")(uri "${KIPRJMOD}/intent.pretty")(options "")'
                '(descr "INTENT badge custom footprints (JLC/EasyEDA geometry)"))\n)\n')
    with open(os.path.join(D, 'sym-lib-table'), 'w', newline='\n') as f:
        f.write('(sym_lib_table\n  (version 7)\n)\n')
    print('project files written')
