#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
#
# end_to_end.py
#
# Takes an XML file (preferrably using TEI conventions) and
# makes:
#
# 1. An XML file with added IDs for elements (if the elements didn't
#    already have ID attributes)
# 2. An FSG file where the transitions are those IDs.
# 3. A dictionary file giving a mapping between IDs and approximate
#    pronunciations in ARPABET
#
#
# The XML file needs to have xml:lang attributes; if tokenization is
# not performed (indicated with <w> elements) it will be attempted
# automatically.  Alignment can be done at any level of analysis; if
# there are, for example, morpheme tags (<m>), you can make that be
# the level of analysis with the option --unit m
#
# TODO: Add numpy standard docstrings to functions
##########################################################################

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse

from readalongs.log import LOGGER
from readalongs.text.add_ids_to_xml import add_ids
from readalongs.text.convert_xml import convert_xml
from readalongs.text.make_dict import make_dict
from readalongs.text.make_fsg import make_fsg
from readalongs.text.tokenize_xml import tokenize_xml
from readalongs.text.util import load_xml, save_txt, save_xml


def end_to_end(xml, input_filename, unit, word_unit, out_orth):
    xml = tokenize_xml(xml)
    xml = add_ids(xml)
    converted_xml, valid = convert_xml(xml, word_unit, out_orth)
    # save_xml("test.xml", converted_xml)
    fsg = make_fsg(converted_xml, input_filename, unit)
    pronouncing_dictionary = make_dict(converted_xml, input_filename, unit)
    return xml, fsg, pronouncing_dictionary


def go(
    input_filename,
    output_xml_filename,
    output_fsg_filename,
    output_dict_filename,
    unit,
    word_unit,
    out_orth,
):
    xml = load_xml(input_filename)
    xml, fsg, dct = end_to_end(xml, input_filename, unit, word_unit, out_orth)
    save_xml(output_xml_filename, xml)
    save_txt(output_fsg_filename, fsg)
    save_txt(output_dict_filename, dct)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert XML to another orthography while preserving tags"
    )
    parser.add_argument("input", type=str, help="Input XML")
    parser.add_argument("output_xml", type=str, help="Output XML file")
    parser.add_argument("output_fsg", type=str, help="Output .jsgf file")
    parser.add_argument("output_dict", type=str, help="Output .dict file")
    parser.add_argument(
        "--unit",
        type=str,
        default="w",
        help="XML tag of the unit of analysis " '(e.g. "w" for word, "m" for morpheme)',
    )
    parser.add_argument(
        "--word_unit",
        type=str,
        default="w",
        help='XML element that represents a word (default: "w")',
    )
    parser.add_argument(
        "--out_orth",
        type=str,
        default="eng-arpabet",
        help='Output orthography (default: "eng-arpabet")',
    )
    parser.add_argument("--debug", action="store_true", help="Enable debugging output")
    args = parser.parse_args()
    if args.debug:
        LOGGER.setLevel("DEBUG")
    go(
        args.input,
        args.output_xml,
        args.output_fsg,
        args.output_dict,
        args.unit,
        args.word_unit,
        args.out_orth,
    )
