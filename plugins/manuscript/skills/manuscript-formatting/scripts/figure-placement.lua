-- Style and optionally collect explicitly marked manuscript figures.
-- Add each figure as a top-level .paper-figure div with one image paragraph
-- followed by one or more caption paragraphs. The image's Markdown alt text
-- becomes accessible alternative text in the exported DOCX.

local FIGURE_CLASS = "paper-figure"

local function has_class(div, wanted)
  for _, class in ipairs(div.classes) do
    if class == wanted then
      return true
    end
  end
  return false
end

local function is_image_paragraph(block)
  if block.t ~= "Para" and block.t ~= "Plain" then
    return false
  end
  return #block.content == 1 and block.content[1].t == "Image"
end

local function style_figure(div)
  local image_seen = false
  local blocks = pandoc.List()
  for _, block in ipairs(div.content) do
    if is_image_paragraph(block) then
      if image_seen then
        error("Each .paper-figure block must contain exactly one image")
      end
      local alt = pandoc.utils.stringify(block.content[1].caption)
      if not alt:match("%S") then
        error("Each .paper-figure image needs non-empty accessible alt text")
      end
      image_seen = true
      blocks:insert(pandoc.Div(
        { block },
        pandoc.Attr("", {}, { ["custom-style"] = "FigureImage" })
      ))
    elseif not image_seen then
      error("A .paper-figure must start with one standalone Markdown image")
    else
      if block.t ~= "Para" and block.t ~= "Plain" then
        error("Figure captions inside .paper-figure must be paragraphs")
      end
      blocks:insert(pandoc.Div(
        { block },
        pandoc.Attr("", {}, { ["custom-style"] = "ImageCaption" })
      ))
    end
  end
  if not image_seen or #blocks < 2 then
    error("A .paper-figure needs one image followed by at least one caption paragraph")
  end
  div.content = blocks
  return div
end

function Pandoc(doc)
  local placement = "inline"
  if doc.meta["figure-placement"] then
    placement = pandoc.utils.stringify(doc.meta["figure-placement"])
  end
  if placement ~= "inline" and placement ~= "end" then
    error("figure-placement must be 'inline' or 'end'")
  end

  local output = pandoc.List()
  local figures = pandoc.List()
  for _, block in ipairs(doc.blocks) do
    if block.t == "Div" and has_class(block, FIGURE_CLASS) then
      local figure = style_figure(block)
      if placement == "end" then
        figures:insert(figure)
      else
        output:insert(figure)
      end
    else
      output:insert(block)
    end
  end

  if #figures > 0 then
    local insertion = #output + 1
    for index, block in ipairs(output) do
      if block.t == "Header" then
        local heading = pandoc.utils.stringify(block):lower()
        if heading == "references" or heading == "bibliography" then
          insertion = index
          break
        end
      elseif block.t == "Div" and block.identifier == "refs" then
        insertion = index
        break
      end
    end
    output:insert(insertion, pandoc.Header(1, "Figures"))
    insertion = insertion + 1
    for _, figure in ipairs(figures) do
      output:insert(insertion, figure)
      insertion = insertion + 1
    end
  end

  doc.blocks = output
  return doc
end
