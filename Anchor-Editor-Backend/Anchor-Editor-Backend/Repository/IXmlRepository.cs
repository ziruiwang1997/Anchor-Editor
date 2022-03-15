using System.Xml.Linq;

namespace Anchor_Editor_Backend.Repository
{
    public interface IXmlRepository
    {
        void uploadXMLFile(XElement xmlFile);
    }
}
