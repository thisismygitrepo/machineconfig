-- DuckDB plugin configuration
-- require("duckdb"):setup()

-- https://yazi-rs.github.io/docs/tips#symlink-in-status
-- https://yazi-rs.github.io/docs/tips#user-group-in-status
-- https://yazi-rs.github.io/docs/tips#username-hostname-in-header


-- Load Status component
function Status:render(area)
	self.area = area

	local left = ui.Line(self:mode())
	local right = ui.Line {}
	local center = ui.Line {}

	-- Add symlink target
	local h = self._current.hovered
	if h and h.link_to then
		center = center .. ui.Span(" -> " .. tostring(h.link_to)):fg("cyan")
	end

	-- Add user:group on Unix
	if h and ya.target_family() == "unix" then
		right = right .. ui.Span(ya.user_name(h.cha.uid) or tostring(h.cha.uid)):fg("magenta")
		right = right .. ui.Span(":"):fg("magenta")
		right = right .. ui.Span(ya.group_name(h.cha.gid) or tostring(h.cha.gid)):fg("magenta")
		right = right .. ui.Span(" ")
	end

	-- Add default status elements
	left = left .. self:size()
	right = self:name() .. right .. self:percentage()

	return {
		ui.Paragraph(area, { left, center }),
		ui.Paragraph(area, { right }):align(ui.Paragraph.RIGHT),
	}
end

-- Load Header component  
function Header:render(area)
	self.area = area
	
	local left = ui.Line {}
	local right = ui.Line {}

	-- Add username@hostname on Unix
	if ya.target_family() == "unix" then
		left = left .. ui.Span(ya.user_name() .. "@" .. ya.host_name() .. ":"):fg("blue")
	end

	-- Add default header elements
	left = left .. self:cwd()
	right = self:tabs()

	return {
		ui.Paragraph(area, { left }),
		ui.Paragraph(area, { right }):align(ui.Paragraph.RIGHT),
	}
end
