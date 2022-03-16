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
using Anchor_Editor_Backend.Models;

namespace Anchor_Editor_Backend.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class XMLFilesController : ControllerBase
    {
        private IXmlRepository _xmlRepository;

        private IXmlDeserializationService _xmlDeserializationService;

        private IAnchorRepository _anchorRepository;

        public XMLFilesController(IAnchorRepository anchorRepository, IXmlRepository xmlRepository, IXmlDeserializationService xmlDeserializationService)
        {
            _anchorRepository = anchorRepository;
            _xmlRepository = xmlRepository;
            _xmlDeserializationService = xmlDeserializationService;
        }

        [HttpPost]
        public IActionResult PostXMLFile([FromBody] XElement request)
        {
            _xmlRepository.OriginalXmlFile = request;

            IList<Anchor> anchorList = _xmlDeserializationService.GetAnchorsAsEnumerableFromXml(_xmlRepository.OriginalXmlFile);

            _anchorRepository.AnchorList = anchorList;

            return Ok("XML Uploaded");
        }

        [HttpGet]
        public IActionResult GetXmlFile()
        {

            return Ok("Default XML");
        }

        
    }
}
