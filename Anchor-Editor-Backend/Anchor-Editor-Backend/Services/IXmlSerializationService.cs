using System.Collections.Generic;
using System.Xml;
using System.Xml.Linq;
using Anchor_Editor_Backend.Models;

namespace Anchor_Editor_Backend.Services
{
    public interface IXmlSerializationService
    {
        XElement GetXmlFromAnchorsAndText(string plainText, IList<Anchor> anchorList);
    }
}
