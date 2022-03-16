using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Text.RegularExpressions;
using Anchor_Editor_Backend.Services;
using Anchor_Editor_Backend.Repository;
using Anchor_Editor_Backend.Models;

namespace Anchor_Editor_Backend.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class AnchorsController : ControllerBase
    {
        private IXmlRepository _xmlRepository;
        private IXmlDeserializationService _xmlDeserializationService;

        public AnchorsController(IXmlRepository xmlRepository, IXmlDeserializationService xmlDeserializationService)
        {
            _xmlRepository = xmlRepository;
            _xmlDeserializationService = xmlDeserializationService;
        }

        [HttpGet]
        public IActionResult GetAllAnchors()
        {
            var originalXmlFile = _xmlRepository.OriginalXmlFile;
            IList<Anchor> anchorList = _xmlDeserializationService.GetAnchorsAsEnumerableFromXml(originalXmlFile);
            return Ok(anchorList);
        }
    }
}
