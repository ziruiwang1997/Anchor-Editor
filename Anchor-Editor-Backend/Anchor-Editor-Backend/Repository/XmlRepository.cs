using System.Xml.Linq;

namespace Anchor_Editor_Backend.Repository
{
    public class XmlRepository : IXmlRepository
    {
        public XElement OriginalXmlFile { get; set; }
        //object IXmlRepository.OriginalXmlFile { get => throw new System.NotImplementedException(); set => throw new System.NotImplementedException(); }

        public void uploadXMLFile(XElement xmlFile)
        {
            OriginalXmlFile = xmlFile;
        }
    }
}
