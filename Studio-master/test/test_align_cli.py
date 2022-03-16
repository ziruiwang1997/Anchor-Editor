#!/usr/bin/env python3

"""
Unit test suite for the readalongs align CLI command
"""

import os
from os.path import exists, join
from unittest import main

from basic_test_case import BasicTestCase
from lxml.html import fromstring
from sound_swallower_stub import SoundSwallowerStub

from readalongs.cli import align, langs


def write_file(filename: str, file_contents: str) -> str:
    """Write file_contents to file filename, and return its name (filename)"""
    with open(filename, mode="w", encoding="utf8") as f:
        f.write(file_contents)
    return filename


class TestAlignCli(BasicTestCase):
    """Unit test suite for the readalongs align CLI command"""

    def test_invoke_align(self):
        """Basic readalongs align invocation and some variants"""
        output = join(self.tempdir, "output")
        with open("image-for-page1.jpg", "wb"):
            pass
        # Run align from plain text
        results = self.runner.invoke(
            align,
            [
                "-s",
                "-o",
                "vtt",
                "-o",  # tests that we can use -o more than once
                "srt:TextGrid,eaf",  # tests that we can give -o multiple values, separated by : or ,
                "-l",
                "fra",
                "--config",
                join(self.data_dir, "sample-config.json"),
                join(self.data_dir, "ej-fra.txt"),
                join(self.data_dir, "ej-fra.m4a"),
                output,
            ],
        )
        # print(results.output)
        self.assertEqual(results.exit_code, 0)
        expected_output_files = [
            "output.smil",
            "output.xml",
            "output.m4a",
            "index.html",
            "output.TextGrid",
            "output.eaf",
            "output_sentences.srt",
            "output_sentences.vtt",
            "output_words.srt",
            "output_words.vtt",
        ]
        for f in expected_output_files:
            self.assertTrue(
                exists(join(output, f)), f"successful alignment should have created {f}"
            )
        with open(join(output, "index.html"), encoding="utf8") as f:
            self.assertIn(
                '<read-along text="output.xml" alignment="output.smil" audio="output.m4a"',
                f.read(),
            )
        self.assertTrue(
            exists(join(output, "tempfiles", "output.tokenized.xml")),
            "alignment with -s should have created tempfiles/output.tokenized.xml",
        )
        self.assertTrue(
            exists(join(output, "assets", "image-for-page1.jpg")),
            "alignment with image files should have copied image-for-page1.jpg to assets",
        )
        self.assertIn("image-for-page2.jpg is accessible ", results.stdout)
        os.unlink("image-for-page1.jpg")
        self.assertFalse(exists("image-for-page1.jpg"))
        # print(results.stdout)

        # Move the alignment output to compare with further down
        # We cannot just output to a different name because changing the output file name
        # changes the contents of the output.
        output1 = output + "1"
        os.rename(output, output1)
        self.assertFalse(exists(output), "os.rename() should have moved dir")

        # Run align again, but on an XML input file with various added DNA text
        results_dna = self.runner.invoke(
            align,
            [
                "-o",
                "xhtml",
                "-s",
                "--config",
                join(self.data_dir, "sample-config.json"),
                join(self.data_dir, "ej-fra-dna.xml"),
                join(self.data_dir, "ej-fra.m4a"),
                output,
            ],
        )
        self.assertEqual(results_dna.exit_code, 0)
        # print(results_dna.stdout)
        self.assertTrue(
            exists(join(output, "output.smil")),
            "successful alignment with DNA should have created output.smil",
        )
        self.assertTrue(
            exists(join(output, "output.xhtml")),
            "successful alignment with -o xhtml should have created output.xhtml",
        )
        self.assertIn("Please copy image-for-page1.jpg to ", results_dna.stdout)
        self.assertFalse(
            exists(join(output, "assets", "image-for-page1.jpg")),
            "image-for-page1.jpg was not on disk, cannot have been copied",
        )

        # Functionally the same as self.assertTrue(filecmp.cmp(f1, f2)), but show where
        # the differences are if the files are not identical
        # Since f2 was created using -o xhtml, we need to substitute .xhtml back to .xml during
        # the comparison of the contents of the .smil files.
        with open(join(output1, "output.smil"), encoding="utf8") as f1, open(
            join(output, "output.smil"), encoding="utf8"
        ) as f2:
            self.assertListEqual(
                list(f1), [line.replace(".xhtml", ".xml") for line in f2]
            )

        # We test error situations in the same test case, since we reuse the same outputs
        results_output_exists = self.runner.invoke(
            align,
            [
                join(self.data_dir, "ej-fra-dna.xml"),
                join(self.data_dir, "ej-fra.m4a"),
                output,
            ],
        )
        self.assertNotEqual(results_output_exists.exit_code, 0)
        self.assertIn(
            "already exists, use -f to overwrite", results_output_exists.output
        )

        # Output path exists as a regular file
        results_output_is_regular_file = self.runner.invoke(
            align,
            [
                join(self.data_dir, "ej-fra-dna.xml"),
                join(self.data_dir, "ej-fra.m4a"),
                join(output, "output.smil"),
            ],
        )
        self.assertNotEqual(results_output_is_regular_file, 0)
        self.assertIn(
            "already exists but is a not a directory",
            results_output_is_regular_file.output,
        )

    def test_align_with_package(self):
        """Test creating a single-file package, with -o html"""

        output = join(self.tempdir, "html")
        with SoundSwallowerStub("t0b0d0p0s0w0:920:1620", "t0b0d0p0s1w0:1620:1690"):
            results_html = self.runner.invoke(
                align,
                [
                    join(self.data_dir, "ej-fra-package.xml"),
                    join(self.data_dir, "ej-fra.m4a"),
                    output,
                    "-o",
                    "html",
                ],
            )
        # print(results_html.output)
        self.assertEqual(results_html.exit_code, 0)
        self.assertTrue(
            exists(join(output, "html.html")),
            "succesful html alignment should have created html/html.html",
        )

        with open(join(output, "html.html"), "rb") as fhtml:
            path_bytes = fhtml.read()
        htmldoc = fromstring(path_bytes)
        b64_pattern = r"data:[\w\/\+]*;base64,\w*"
        self.assertRegex(
            htmldoc.body.xpath("//read-along")[0].attrib["text"], b64_pattern
        )
        self.assertRegex(
            htmldoc.body.xpath("//read-along")[0].attrib["alignment"], b64_pattern
        )
        self.assertRegex(
            htmldoc.body.xpath("//read-along")[0].attrib["audio"], b64_pattern
        )

    def not_test_permission_denied(self):
        """Non-portable test to make sure denied permission triggers an error -- disabled"""
        # This test is not stable, just disable it.
        # It apparently also does not work correctly on M1 Macs either, even in Docker.

        import platform

        if platform.system() == "Windows" or "WSL2" in platform.release():
            # Cannot change the permission on a directory in Windows though
            # os.mkdir() or os.chmod(), so skip this test
            return
        dirname = join(self.tempdir, "permission_denied")
        os.mkdir(dirname, mode=0o444)
        results = self.runner.invoke(
            align,
            [
                "-f",
                join(self.data_dir, "ej-fra-dna.xml"),
                join(self.data_dir, "ej-fra.m4a"),
                dirname,
            ],
        )
        self.assertNotEqual(results, 0)
        self.assertIn("Cannot write into output folder", results.output)

    def test_langs_cmd(self):
        """Validates that readalongs langs lists all in-langs that can map to eng-arpabet"""
        results = self.runner.invoke(langs)
        self.assertEqual(results.exit_code, 0)
        self.assertIn("crg-tmd", results.stdout)
        self.assertIn("crg-dv ", results.stdout)
        self.assertNotIn("crg ", results.stdout)
        self.assertNotIn("fn-unicode", results.stdout)

    def test_align_english(self):
        """Validates that LexiconG2P works for English language alignment"""

        input_filename = write_file(
            join(self.tempdir, "input"),
            "This is some text that we will run through the English lexicon "
            "grapheme to morpheme approach.",
        )
        output_dir = join(self.tempdir, "eng-output")
        # Run align from plain text
        with SoundSwallowerStub("word:0:1000"):
            self.runner.invoke(
                align,
                [
                    "-s",
                    "-l",
                    "eng",
                    input_filename,
                    join(self.data_dir, "ej-fra.m4a"),
                    output_dir,
                ],
            )

        g2p_ref = '<s id="t0b0d0p0s0"><w id="t0b0d0p0s0w0" ARPABET="DH IH S">This</w> <w id="t0b0d0p0s0w1" ARPABET="IH Z">is</w> <w id="t0b0d0p0s0w2" ARPABET="S AH M">some</w> <w id="t0b0d0p0s0w3" ARPABET="T EH K S T">text</w> <w id="t0b0d0p0s0w4" ARPABET="DH AE T">that</w> <w id="t0b0d0p0s0w5" ARPABET="W IY">we</w> <w id="t0b0d0p0s0w6" ARPABET="W IH L">will</w> <w id="t0b0d0p0s0w7" ARPABET="R AH N">run</w> <w id="t0b0d0p0s0w8" ARPABET="TH R UW">through</w> <w id="t0b0d0p0s0w9" ARPABET="DH AH">the</w> <w id="t0b0d0p0s0w10" ARPABET="IH NG G L IH SH">English</w> <w id="t0b0d0p0s0w11" ARPABET="L EH K S IH K AA N">lexicon</w> <w id="t0b0d0p0s0w12" ARPABET="G R AE F IY M">grapheme</w> <w id="t0b0d0p0s0w13" ARPABET="T UW">to</w> <w id="t0b0d0p0s0w14" ARPABET="M AO R F IY M">morpheme</w> <w id="t0b0d0p0s0w15" ARPABET="AH P R OW CH">approach</w>.</s>'

        tokenized_file = join(
            self.tempdir, "eng-output", "tempfiles", "eng-output.g2p.xml"
        )
        with open(tokenized_file, "r", encoding="utf8") as f:
            tok_output = f.read()

        self.assertIn(g2p_ref, tok_output)

    def test_invalid_config(self):
        """unit testing for invalid config specifications"""

        # --config parameter needs to be <somefile>.json, text with .txt instead
        result = self.runner.invoke(
            align,
            [
                "--config",
                join(self.data_dir, "fra.txt"),
                join(self.data_dir, "fra.txt"),
                join(self.data_dir, "noise.mp3"),
                join(self.tempdir, "out-invalid-config-1"),
            ],
        )
        self.assertIn("must be in JSON format", result.stdout)

        # --config parameters needs to contain valid json, test with garbage
        config_file = join(self.tempdir, "bad-config.json")
        with open(config_file, "w", encoding="utf8") as f:
            print("not valid json", file=f)
        result = self.runner.invoke(
            align,
            [
                "--config",
                config_file,
                join(self.data_dir, "fra.txt"),
                join(self.data_dir, "noise.mp3"),
                join(self.tempdir, "out-invalid-config-2"),
            ],
        )
        self.assertIn("is not in valid JSON format", result.stdout)

    def test_bad_anchors(self):
        """Make sure invalid anchors yield appropriate errors"""

        xml_text = """<?xml version='1.0' encoding='utf-8'?>
            <TEI><text xml:lang="fra"><body><p>
            <anchor /><s>Bonjour.</s><anchor time="invalid"/>
            </p></body></text></TEI>
        """
        xml_file = join(self.tempdir, "bad-anchor.xml")
        with open(xml_file, "w", encoding="utf8") as f:
            print(xml_text, file=f)
        bad_anchors_result = self.runner.invoke(
            align,
            [
                xml_file,
                join(self.data_dir, "noise.mp3"),
                join(self.tempdir, "out-bad-anchors"),
            ],
        )
        for msg in [
            'missing "time" attribute',
            'invalid "time" attribute "invalid"',
            "Could not parse all anchors",
            "Aborting.",
        ]:
            self.assertIn(msg, bad_anchors_result.stdout)

    def test_misc_align_errors(self):
        """Test calling readalongs align with misc CLI errors"""
        results = self.runner.invoke(
            align,
            [
                join(self.data_dir, "ej-fra.txt"),
                join(self.data_dir, "ej-fra.m4a"),
                join(self.tempdir, "out-missing-l"),
            ],
        )
        self.assertNotEqual(results.exit_code, 0)
        self.assertIn("No input language specified", results.output)

        with SoundSwallowerStub("[NOISE]:0:1"):
            results = self.runner.invoke(
                align,
                [
                    join(self.data_dir, "fra-prepared.xml"),
                    join(self.data_dir, "noise.mp3"),
                    join(self.tempdir, "noise-only"),
                ],
            )
        self.assertNotEqual(results.exit_code, 0)
        self.assertIn("produced 0 segments", results.output)

        with SoundSwallowerStub(
            "[NOISE]:0:1", "w0:1:1000", "<sil>:1000:1100", "w1:1100:2000"
        ):
            results = self.runner.invoke(
                align,
                [
                    join(self.data_dir, "ej-fra.xml"),
                    join(self.data_dir, "ej-fra.m4a"),
                    join(self.tempdir, "two-words"),
                ],
            )
        # print(results.output)
        # We don't check results.exit_code since that's a soft warning, not a hard error
        self.assertIn("produced 2 segments", results.output)
        self.assertIn(
            "Alignment produced a different number of segments and tokens than were in the input.",
            results.output,
        )

    def test_infer_plain_text_or_xml(self):
        """align -i is obsolete, now we infer plain text vs XML; test that!"""

        # plain text with guess by contents
        infile1 = write_file(join(self.tempdir, "infile1"), "some plain text")
        with SoundSwallowerStub("word:0:1"):
            results = self.runner.invoke(
                align,
                [
                    infile1,
                    join(self.data_dir, "noise.mp3"),
                    join(self.tempdir, "outdir1"),
                ],
            )
        self.assertNotEqual(results.exit_code, 0)
        # This error message confirms it's being processed as plain text
        self.assertIn("No input language specified for plain text", results.output)

        # plain text by extension
        infile2 = write_file(join(self.tempdir, "infile2.txt"), "<?xml but .txt")
        with SoundSwallowerStub("word:0:1"):
            results = self.runner.invoke(
                align,
                [
                    infile2,
                    join(self.data_dir, "noise.mp3"),
                    join(self.tempdir, "outdir2"),
                ],
            )
        self.assertNotEqual(results.exit_code, 0)
        # This error message confirms it's being processed as plain text
        self.assertIn("No input language specified for plain text", results.output)

        # XML with guess by contents
        infile3 = write_file(
            join(self.tempdir, "infile3"),
            "<?xml version='1.0' encoding='utf-8'?><text>blah blah</text>",
        )
        with SoundSwallowerStub("word:0:1"):
            results = self.runner.invoke(
                align,
                [
                    infile3,
                    join(self.data_dir, "noise.mp3"),
                    join(self.tempdir, "outdir3"),
                ],
            )
        self.assertEqual(results.exit_code, 0)

        # XML with guess by contents, but with content error
        infile4 = write_file(
            join(self.tempdir, "infile4"),
            "<?xml version='1.0' encoding='utf-8'?><text>blah blah</bad_tag>",
        )
        with SoundSwallowerStub("word:0:1"):
            results = self.runner.invoke(
                align,
                [
                    infile4,
                    join(self.data_dir, "noise.mp3"),
                    join(self.tempdir, "outdir4"),
                ],
            )
        self.assertNotEqual(results.exit_code, 0)
        self.assertIn("Error parsing XML", results.output)

        # XML by file extension
        infile5 = write_file(join(self.tempdir, "infile5.xml"), "Not XML!")
        with SoundSwallowerStub("word:0:1"):
            results = self.runner.invoke(
                align,
                [
                    infile5,
                    join(self.data_dir, "noise.mp3"),
                    join(self.tempdir, "outdir5"),
                ],
            )
        self.assertNotEqual(results.exit_code, 0)
        self.assertIn("Error parsing XML", results.output)

    def test_obsolete_switches(self):
        # Giving -i switch generates an obsolete-switch error message
        with SoundSwallowerStub("word:0:1"):
            results = self.runner.invoke(
                align,
                [
                    "-i",
                    join(self.data_dir, "fra.txt"),
                    join(self.data_dir, "noise.mp3"),
                    join(self.tempdir, "outdir6"),
                ],
            )
        self.assertNotEqual(results.exit_code, 0)
        self.assertIn("is obsolete.", results.output)

        # Giving --g2p-verbose switch generates an obsolete-switch error message
        with SoundSwallowerStub("word:0:1"):
            results = self.runner.invoke(
                align,
                [
                    "--g2p-verbose",
                    join(self.data_dir, "fra.txt"),
                    join(self.data_dir, "noise.mp3"),
                    join(self.tempdir, "outdir7"),
                ],
            )
        self.assertNotEqual(results.exit_code, 0)
        self.assertIn("is obsolete.", results.output)

        # Giving --g2p-fallback switch generates an obsolete-switch error message
        with SoundSwallowerStub("word:0:1"):
            results = self.runner.invoke(
                align,
                [
                    "--g2p-fallback",
                    "fra:end:und",
                    join(self.data_dir, "fra.txt"),
                    join(self.data_dir, "noise.mp3"),
                    join(self.tempdir, "outdir8"),
                ],
            )
        self.assertNotEqual(results.exit_code, 0)
        self.assertIn("is obsolete.", results.output)


if __name__ == "__main__":
    main()
