#!/usr/bin/env python3
"""gen.py <php|ruby|java|csharp> <out-path>"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from models_schema import MODELS, parse, snake, pascal

lang, out = sys.argv[1], pathlib.Path(sys.argv[2])

def php():
    out.mkdir(parents=True, exist_ok=True)
    for name, (doc, fields) in MODELS.items():
        params, builds, docs = [], [], []
        for f, t in fields:
            nullable, kind, inner = parse(t)
            if kind == "list":
                phpt = "array"; docs.append(f"     * @param list<{'string' if inner == 'str' else inner}> ${f}")
                src = f"array_map(static fn (array $x): {inner} => {inner}::fromArray($x), $d['{f}'] ?? [])" if inner not in ("str",) else f"$d['{f}'] ?? []"
            elif kind == "model":
                phpt = ("?" if nullable else "") + inner
                src = f"isset($d['{f}']) ? {inner}::fromArray($d['{f}']) : null" if nullable else f"{inner}::fromArray($d['{f}'])"
            else:
                base = {"str": "string", "int": "int", "float": "float", "bool": "bool"}[inner]
                phpt = ("?" if nullable else "") + base
                cast = {"string": "(string)", "int": "(int)", "float": "(float)", "bool": "(bool)"}[base]
                src = f"isset($d['{f}']) ? {cast} $d['{f}'] : null" if nullable else f"{cast} $d['{f}']"
            params.append(f"        public readonly {phpt} ${f},")
            builds.append(f"            {f}: {src},")
        docblock = ("    /**\n" + "\n".join(docs) + "\n     */\n") if docs else ""
        body = f"""<?php

declare(strict_types=1);

namespace BuyProxy\\Models;

/** {doc} */
final class {name}
{{
{docblock}    public function __construct(
{chr(10).join(params)}
    ) {{
    }}

    /** @param array<string, mixed> $d */
    public static function fromArray(array $d): self
    {{
        return new self(
{chr(10).join(builds)}
        );
    }}
}}
"""
        (out / f"{name}.php").write_text(body)

def ruby():
    lines = ["# frozen_string_literal: true", "", "# Generated from the BuyProxy API schema — do not edit by hand.", "module BuyProxy", "  module Models"]
    for name, (doc, fields) in MODELS.items():
        attrs = ", ".join(f":{snake(f)}" for f, _ in fields)
        lines += [f"    # {doc}", f"    class {name}", f"      attr_reader {attrs}", "", "      def initialize(**attrs)"]
        for f, _ in fields:
            lines.append(f"        @{snake(f)} = attrs[:{snake(f)}]")
        lines += ["      end", "", "      def self.from_hash(h)", "        new("]
        for i, (f, t) in enumerate(fields):
            nullable, kind, inner = parse(t)
            if kind == "list":
                src = f"(h['{f}'] || []).map {{ |x| {inner}.from_hash(x) }}" if inner != "str" else f"h['{f}'] || []"
            elif kind == "model":
                src = f"h['{f}'] ? {inner}.from_hash(h['{f}']) : nil" if nullable else f"{inner}.from_hash(h['{f}'])"
            else:
                src = f"h['{f}']"
            comma = "," if i < len(fields) - 1 else ""
            lines.append(f"          {snake(f)}: {src}{comma}")
        lines += ["        )", "      end", "", "      def to_h", "        {"]
        for i, (f, _) in enumerate(fields):
            comma = "," if i < len(fields) - 1 else ""
            lines.append(f"          {snake(f)}: @{snake(f)}{comma}")
        lines += ["        }", "      end", "    end", ""]
    lines += ["  end", "end", ""]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))

def java():
    out.mkdir(parents=True, exist_ok=True)
    jt = {"str": "String", "int": "int", "float": "double", "bool": "boolean"}
    jt_null = {"str": "String", "int": "Integer", "float": "Double", "bool": "Boolean"}
    for name, (doc, fields) in MODELS.items():
        comps = []
        for f, t in fields:
            nullable, kind, inner = parse(t)
            if kind == "list":
                typ = f"List<{'String' if inner == 'str' else inner}>"
            elif kind == "model":
                typ = inner
            else:
                typ = (jt_null if nullable else jt)[inner]
            nn = "@Nullable " if nullable else ""
            comps.append(f"        {nn}{typ} {f}")
        uses_list = any(parse(t)[1] == "list" for _, t in fields)
        body = f"""package org.buyproxy.model;

{"import java.util.List;" + chr(10) if uses_list else ""}import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import org.jspecify.annotations.Nullable;

/** {doc} */
@JsonIgnoreProperties(ignoreUnknown = true)
public record {name}(
{("," + chr(10)).join(comps)}) {{}}
"""
        (out / f"{name}.java").write_text(body)

def csharp():
    ct = {"str": "string", "int": "int", "float": "double", "bool": "bool"}
    lines = ["// Generated from the BuyProxy API schema — do not edit by hand.", "using System.Collections.Generic;", "", "namespace BuyProxy.Models;", ""]
    for name, (doc, fields) in MODELS.items():
        comps = []
        for f, t in fields:
            nullable, kind, inner = parse(t)
            if kind == "list":
                typ = f"IReadOnlyList<{'string' if inner == 'str' else inner}>"
            elif kind == "model":
                typ = inner + ("?" if nullable else "")
            else:
                typ = ct[inner] + ("?" if nullable else "")
            comps.append(f"{typ} {pascal(f)}")
        lines += [f"/// <summary>{doc}</summary>", f"public sealed record {name}(" + ", ".join(comps) + ");", ""]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))

{"php": php, "ruby": ruby, "java": java, "csharp": csharp}[lang]()
print(f"generated {lang} models → {out}")
