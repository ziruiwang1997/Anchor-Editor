using Anchor_Editor_Backend.Models;
using System.Collections.Generic;
using System.Xml;
using System.Xml.Linq;

namespace Anchor_Editor_Backend.Services
{
    public class XmlSerializationService : IXmlSerializationService
    {
        public XElement GetXmlFromAnchorsAndText(string plainText, IList<Anchor> anchorList, XElement originalXmlFile)
        {
            var originalXmlAsString = originalXmlFile.ToString();

            IList<string> HeaderAndTailList = GetHeaderAndTailOfXmlString(originalXmlAsString);
            string headString = HeaderAndTailList[0];
            string tailString = HeaderAndTailList[1];

            throw new System.NotImplementedException();
        }

        private IList<string> GetHeaderAndTailOfXmlString(string xmlString)
        {
            IList<string> result = new List<string>();

            for (int counter = 0; counter < xmlString.Length; counter++)
            {
                if (xmlString[counter] == '<')
                {
                    if (counter + 6 < xmlString.Length && xmlString.Substring(counter, 6) == "<body>")
                    {
                        result.Add(xmlString.Substring(0, counter));
                    }

                    if (counter + 7 < xmlString.Length && xmlString.Substring(counter, 7) == "</body>")
                    {
                        result.Add(xmlString.Substring(counter));
                    }
                }
            }
            
            return result;
        }
    }
}
