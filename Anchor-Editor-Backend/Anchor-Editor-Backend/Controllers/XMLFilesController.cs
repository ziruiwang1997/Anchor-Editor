using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Text.RegularExpressions;
using System.Net.Http;
using System.Xml;
using System.Xml.Linq;
using Anchor_Editor_Backend.Repository;
using Anchor_Editor_Backend.Services;

namespace Anchor_Editor_Backend.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class XMLFilesController : ControllerBase
    {
        private IXmlRepository _textRepository;
        private IXmlDeserializationService _xmlDeserializationService;
        public XMLFilesController(IXmlRepository textRepository, IXmlDeserializationService xmlDeserializationService)
        {
            _textRepository = textRepository;
            _xmlDeserializationService = xmlDeserializationService;
        }

        [HttpPost]
        public IActionResult PostXMLFile([FromBody] XElement request)
        {
            _textRepository.uploadXMLFile(request);
            var plainText = _xmlDeserializationService.GetPlainTextAsStringFromXml(request);
            return Ok(plainText);
        }
    }
}
