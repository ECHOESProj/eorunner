<?xml version="1.0" encoding="UTF-8"?>
<StyledLayerDescriptor xmlns="http://www.opengis.net/sld" xmlns:sld="http://www.opengis.net/sld" xmlns:gml="http://www.opengis.net/gml" version="1.0.0" xmlns:ogc="http://www.opengis.net/ogc">
  <UserLayer>
    <sld:LayerFeatureConstraints>
      <sld:FeatureTypeConstraint/>
    </sld:LayerFeatureConstraints>
    <sld:UserStyle>
      <sld:Name>NDWI_sgement</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Rule>
			<sld:RasterSymbolizer>
				<sld:Geometry>
					<ogc:PropertyName>grid</ogc:PropertyName>
				</sld:Geometry>
				<sld:Opacity>1</sld:Opacity>
				<sld:ColorMap>
					<sld:ColorMapEntry color="#ff00ff" label="0" opacity="1.0" quantity="0"/>
					<sld:ColorMapEntry color="#0000cd" label="1" opacity="1.0" quantity="1"/>
				</sld:ColorMap>
			</sld:RasterSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </UserLayer>
</StyledLayerDescriptor>
