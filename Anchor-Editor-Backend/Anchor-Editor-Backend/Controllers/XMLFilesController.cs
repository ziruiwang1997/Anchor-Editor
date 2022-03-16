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
        private IXmlRepository _xmlRepository;

        private IXmlDeserializationService _xmlDeserializationService;
        public XMLFilesController(IXmlRepository xmlRepository, IXmlDeserializationService xmlDeserializationService)
        {
            _xmlRepository = xmlRepository;
            _xmlDeserializationService = xmlDeserializationService;
        }

        [HttpPost]
        public IActionResult PostXMLFile([FromBody] XElement request)
        {
            _xmlRepository.uploadXMLFile(request);
            
            return Ok("XML Uploaded");
        }

        [HttpGet]
        public IActionResult GetPlainText()
        {
            var originalXmlFile = _xmlRepository.OriginalXmlFile;
            string plainText = _xmlDeserializationService.GetPlainTextAsStringFromXml(originalXmlFile);
            return Ok(plainText);
        }
    }
}
