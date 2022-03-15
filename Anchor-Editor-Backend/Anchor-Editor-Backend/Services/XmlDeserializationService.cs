using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Text.RegularExpressions;
using System.Net.Http;
using System.Xml;
using System.Xml.Linq;
using Anchor_Editor_Backend.Repository;

namespace Anchor_Editor_Backend.Services
{
    public class XmlDeserializationService : IXmlDeserializationService
    {
        public XmlDeserializationService()
        {

        }

        public string GetPlainTextAsStringFromXml(XElement xmlFile)
        { 
            return xmlFile.ToString();
        }
    }
}
