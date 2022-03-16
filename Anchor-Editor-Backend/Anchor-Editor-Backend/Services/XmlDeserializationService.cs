using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Text.RegularExpressions;
using System.Net.Http;
using System.Xml;
using System.Xml.Linq;
using Anchor_Editor_Backend.Repository;
using System.Collections.Generic;
using System;
using System.Linq;

namespace Anchor_Editor_Backend.Services
{
    public class XmlDeserializationService : IXmlDeserializationService
    {
        public XmlDeserializationService()
        {

        }

        public string GetPlainTextAsStringFromXml(XElement xmlFile)
        {
            string plainText = "";

            XmlDocument originalXmlDocument = new XmlDocument();
            var originalXmlAsString = xmlFile.ToString();
            originalXmlDocument.LoadXml(originalXmlAsString);

            XmlNodeList paragraphList = originalXmlDocument.DocumentElement.GetElementsByTagName("p");

            foreach (XmlNode paragraphNode in paragraphList)
            {
                XmlDocument sentencesXml = new XmlDocument();
                sentencesXml.LoadXml("<paragraphRoot>" + paragraphNode.InnerXml + "</paragraphRoot>");
                XmlNodeList sentenceList = sentencesXml.DocumentElement.GetElementsByTagName("s");
                foreach (XmlNode sentenceNode in sentenceList)
                {
                    string sentence = sentenceNode.InnerText;
                    plainText = plainText + sentence + "\n";
                }
                plainText = plainText + "\n\n";
            }

            

            return plainText;

        }
    }
}
