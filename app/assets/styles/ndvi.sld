<?xml version="1.0" encoding="UTF-8"?>
<sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" version="1.0.0">
	<sld:NamedLayer>
		<sld:Name>NDVI_output</sld:Name>
		<sld:UserStyle>
			<sld:Name>NDVI_output</sld:Name>
			<sld:FeatureTypeStyle>
				<sld:Name>name</sld:Name>
				<sld:Rule>
					<sld:RasterSymbolizer>
						<sld:ChannelSelection>
							<sld:GrayChannel>
								<sld:SourceChannelName>1</sld:SourceChannelName>
								<sld:ContrastEnhancement>
									<sld:GammaValue>1.0</sld:GammaValue>
								</sld:ContrastEnhancement>
							</sld:GrayChannel>
						</sld:ChannelSelection>
						<sld:ColorMap>
							<sld:ColorMapEntry color="#877026" label="Inanimate Object" opacity="1.0" quantity="-1"/>
							<sld:ColorMapEntry color="#958934" label="Unhealthy Vegetation" opacity="1.0" quantity="0"/>
							<sld:ColorMapEntry color="#9fc55a" label="Moderatly Healthy Vegetation" opacity="1.0" quantity="0.33"/>
							<sld:ColorMapEntry color="#397624" label="Healthy Vegetation" opacity="1.0" quantity="0.66"/>
							<sld:ColorMapEntry color="#10401b" label="Very Healthy Vegeation" opacity="1.0" quantity="1"/>
						</sld:ColorMap>
						<sld:ContrastEnhancement/>
					</sld:RasterSymbolizer>
				</sld:Rule>
			</sld:FeatureTypeStyle>
		</sld:UserStyle>
	</sld:NamedLayer>
</sld:StyledLayerDescriptor>
