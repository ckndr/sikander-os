Add-Type -AssemblyName System.Drawing

function Create-RoundedRectanglePath {
    param([float]$x, [float]$y, [float]$width, [float]$height, [float]$radius)
    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    $diameter = $radius * 2
    $path.AddArc($x, $y, $diameter, $diameter, 180, 90)
    $path.AddArc($x + $width - $diameter, $y, $diameter, $diameter, 270, 90)
    $path.AddArc($x + $width - $diameter, $y + $height - $diameter, $diameter, $diameter, 0, 90)
    $path.AddArc($x, $y + $height - $diameter, $diameter, $diameter, 90, 90)
    $path.CloseFigure()
    return $path
}

function Render-SikanderIcon {
    param(
        [int]$size,
        [string]$outputPath,
        [bool]$isMaskable
    )

    $bmp = New-Object System.Drawing.Bitmap($size, $size, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
    $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality

    $scale = [float]$size / 512.0

    # 1. Background
    $bgBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(255, 7, 9, 14)) # #07090e
    $g.FillRectangle($bgBrush, 0, 0, $size, $size)

    if (-not $isMaskable) {
        # Outer rounded tile for standard icons
        $outerRadius = 96.0 * $scale
        $outerPath = Create-RoundedRectanglePath (16.0 * $scale) (16.0 * $scale) (480.0 * $scale) (480.0 * $scale) $outerRadius
        $tileBgBrush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
            (New-Object System.Drawing.PointF(0, 0)),
            (New-Object System.Drawing.PointF($size, $size)),
            [System.Drawing.Color]::FromArgb(255, 14, 20, 34),
            [System.Drawing.Color]::FromArgb(255, 7, 9, 14)
        )
        $g.FillPath($tileBgBrush, $outerPath)

        $borderPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(180, 0, 242, 254), (6.0 * $scale))
        $g.DrawPath($borderPen, $outerPath)
    }

    # Scale factor for inner gem (maskable needs slightly more padding to stay in safe-zone)
    $gemScale = if ($isMaskable) { 0.74 } else { 0.86 }
    $cx = [float]$size / 2.0
    $cy = [float]$size / 2.0
    $gemSize = 270.0 * $scale * $gemScale
    $gemRadius = 60.0 * $scale * $gemScale

    # Gem background gradient (Cyan to Purple/Violet)
    $gemRect = New-Object System.Drawing.RectangleF(($cx - $gemSize/2.0), ($cy - $gemSize/2.0), $gemSize, $gemSize)
    $gemPath = Create-RoundedRectanglePath $gemRect.X $gemRect.Y $gemRect.Width $gemRect.Height $gemRadius

    # Outer ambient glow of gem
    for ($i = 3; $i -ge 1; $i--) {
        $alpha = [int](35 / $i)
        $glowPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb($alpha, 0, 242, 254), (12.0 * $i * $scale))
        $g.DrawPath($glowPen, $gemPath)
    }

    $gemBrush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
        (New-Object System.Drawing.PointF($gemRect.Left, $gemRect.Top)),
        (New-Object System.Drawing.PointF($gemRect.Right, $gemRect.Bottom)),
        [System.Drawing.Color]::FromArgb(255, 0, 242, 254), # #00f2fe
        [System.Drawing.Color]::FromArgb(255, 139, 92, 246) # #8b5cf6
    )
    $g.FillPath($gemBrush, $gemPath)

    # Inner border for gem
    $innerGemPen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(150, 255, 255, 255), (2.5 * $scale))
    $g.DrawPath($innerGemPen, $gemPath)

    # 3. High-Tech Lightning Bolt
    $origPoints = @(
        (New-Object System.Drawing.PointF(276, 146)),
        (New-Object System.Drawing.PointF(176, 274)),
        (New-Object System.Drawing.PointF(252, 274)),
        (New-Object System.Drawing.PointF(236, 366)),
        (New-Object System.Drawing.PointF(336, 238)),
        (New-Object System.Drawing.PointF(260, 238))
    )

    $scaledPoints = [System.Drawing.PointF[]]::new(6)
    for ($i = 0; $i -lt 6; $i++) {
        $px = $cx + ($origPoints[$i].X - 256.0) * $scale * $gemScale * 1.05
        $py = $cy + ($origPoints[$i].Y - 256.0) * $scale * $gemScale * 1.05
        $scaledPoints[$i] = New-Object System.Drawing.PointF($px, $py)
    }

    # Bolt shadow
    $shadowPoints = [System.Drawing.PointF[]]::new(6)
    for ($i = 0; $i -lt 6; $i++) {
        $shadowPoints[$i] = New-Object System.Drawing.PointF($scaledPoints[$i].X, ($scaledPoints[$i].Y + 4.0 * $scale))
    }
    $boltShadowBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(90, 0, 0, 0))
    $g.FillPolygon($boltShadowBrush, $shadowPoints)

    # Bolt solid fill
    $boltBrush = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
        (New-Object System.Drawing.PointF($cx, $gemRect.Top)),
        (New-Object System.Drawing.PointF($cx, $gemRect.Bottom)),
        [System.Drawing.Color]::FromArgb(255, 255, 255, 255),
        [System.Drawing.Color]::FromArgb(255, 224, 250, 255)
    )
    $g.FillPolygon($boltBrush, $scaledPoints)

    # Save PNG
    $bmp.Save($outputPath, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose()
    $bmp.Dispose()
    Write-Output "Successfully generated: $outputPath"
}

Render-SikanderIcon -size 192 -outputPath "i:\sikander-os\icons\icon-192.png" -isMaskable $false
Render-SikanderIcon -size 512 -outputPath "i:\sikander-os\icons\icon-512.png" -isMaskable $false
Render-SikanderIcon -size 192 -outputPath "i:\sikander-os\icons\icon-maskable-192.png" -isMaskable $true
Render-SikanderIcon -size 512 -outputPath "i:\sikander-os\icons\icon-maskable-512.png" -isMaskable $true
