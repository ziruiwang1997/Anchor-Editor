using System.Xml.Linq;
namespace Anchor_Editor_Backend.Services
{
    public interface IXmlDeserializationService
    {
        public string GetPlainTextAsStringFromXml(XElement xmlFile);
    }
}
